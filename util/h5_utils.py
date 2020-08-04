
import h5py as h5
from collections import defaultdict
import os
import multiprocessing
import psutil
import numpy as np

def multi_merge_h5_data(h5_paths_tasks, num_proc=None):
    '''This function serves as a wrapper for merge_h5_data where
    it will call merge_h5_data using a multiprocessing pool
    '''
    if not num_proc:
        num_proc = psutil.cpu_count(logical=False)
    
    print("Starting data collection with %d processes" % num_proc)
    with multiprocessing.Pool(processes=num_proc) as pool:
        results = pool.map(merge_h5_data, h5_paths_tasks)

    merged_dicts = [val[0] for val in results]
    raw_dicts = [val[1] for val in results]
    
    return (merged_dicts, raw_dicts)


def merge_h5_data(h5_paths):
    '''Handles iterating over h5_paths, loading the h5 file, and merging it into a dictionary
    This is called given all the h5_paths of a particular configuration
    
    Inputs:
        h5_paths: A list of file paths for h5 files to merge
    
    Returns:
        A dictionary containing all the info across all the h5 files
    '''
    merge_h5_dict = defaultdict(dict)
    raw_h5_dict = defaultdict(dict)

    for h5_path in h5_paths:
        print("Starting %s..." % h5_path)
        h5_dict = load_h5_to_dict(h5_path)

        # iterate over each region and then event
        # NOTE: 'Runtime' is considered an event right now
        for reg in h5_dict:
            for ev, data in h5_dict[reg].items():
                # True if we saw this event already
                # This is only problematic if this event isn't 'Runtime', meaning a
                # a counter was collected across multiple runs
                # If this is the case, we do nothing and "throw" it out
                if ev in raw_h5_dict[reg]:
                    # Otherwise we simply concat the runtime to be averaged out later
                    if ev == 'Runtime':
                        raw_h5_dict[reg][ev] = np.concatenate((raw_h5_dict[reg][ev], data), axis=1)
                    else:
                        print("\nWARNING: %s is attempting to report %s  which is already found elsewhere." % (h5_path, ev))
                        print("This additional event will be ignored.")
                else:
                    raw_h5_dict[reg][ev] = data

    # Iterate over everything again and take the mean
    # Final mapping should be: region(string)->event(string)->value(1x1 float)
    for reg in raw_h5_dict:
        for ev in raw_h5_dict[reg]:
            merge_h5_dict[reg][ev] = np.mean(raw_h5_dict[reg][ev])

    
    return (merge_h5_dict, raw_h5_dict)

def load_h5_to_dict(h5_path):
    '''Loads the given h5 file up and parses it into a dictionary
    '''
    h5_dict = {}
    with h5.File(h5_path) as h5_file:
        for reg_key in h5_file.keys():
            h5_dict[reg_key] = {}
            for ev_key in h5_file[reg_key].keys():
                # Grabs the data and assigns it
                data = h5_file[reg_key][ev_key][:]

                # Grab everything BUT the last column
                # This last column only has zeros
                data = data[:, 0, :-1]
                data = data.astype(float)

                h5_dict[reg_key][ev_key] = data
    
    return h5_dict

def get_event_subset(merged_h5_dicts, configs):
    '''Iterates over a list of dictionaries (given by merge_h5_data) and
    performs validation on the dictionary as well as determining the smallest
    subset of events across all the dictionaries

    Inputs:
        merged_h5_dicts: list of dictionaries returned by merge_h5_data
        configs: dictionary containing information on the config we're parsing
    '''

    # Iterate over each dictionary
    event_sets = []
    for i, h5_dict in enumerate(merged_h5_dicts):
        try:
            # Perform a validation test and gets a set of the events this dictionary has
            # Throws an error if validation fails
            # See valdiate_region_events for more info
            event_set = validate_region_events(h5_dict)
            event_sets.append(event_set)
            print("Job config with processes=%d passed validation." % configs[i])
        except: continue
    
    # We take the first event set as our starting point
    event_subset = event_sets[0]
    # Iterate over the rest
    for i in range(1, len(event_sets)):
        # True if the current event set has more or less events that the upcoming event set
        # This occurs if not all runs collected all the same events
        # We continue with the intersection of the events producing a subset of events that
        # all configurations have
        if event_subset != event_sets[i]:
            print("WARNING: Job config with processes=%d had different events." % configs[i])
            print("Will continue using a subset of events...")
            event_subset = event_subset.intersection(event_sets[i])
            print(len(event_subset))
    
    return event_subset

def clean_and_get_regions(merged_h5_dicts, configs):
    '''Iterates over a list of dicitonaries and remove any invalid regions
    '''

    for i, h5_dict in enumerate(merged_h5_dicts):
        regions_to_remove = []

        # A region is invalid if it's runtime is negative or zero
        for reg in h5_dict:
            if h5_dict[reg]['Runtime'] <= 0.0:
                regions_to_remove.append(reg)
        
        for reg in regions_to_remove:
            print("Removing %s from job config with processes=%d for having a zero runtime." % (reg, configs[i]))
            del h5_dict[reg]
    
    reg_set = validate_regions(merged_h5_dicts)

    return reg_set

def validate_region_events(h5_dict):
    event_set = set()
    
    # Iterate over each region and add their events to a set
    for reg in h5_dict:
        for ev in h5_dict[reg]:
            event_set.add(ev)
    
    # Assert that each region has all the same counters
    for reg in h5_dict:
        assert set(h5_dict[reg].keys()) == event_set
    
    return event_set

def validate_regions(h5_dicts):
    reg_set = set()
    
    # Iterates over each dicitonary and gets their regions
    for h5_dict in h5_dicts:
        for reg in h5_dict:
            reg_set.add(reg)
    
    # Create largest common subset
    for h5_dict in h5_dicts:
        reg_set = reg_set.intersection(h5_dict.keys())
    
    return reg_set

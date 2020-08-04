###Utility Functions####

import h5py
import argparse
import sys
import numpy as np
import matplotlib
import csv
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import os.path
import collections #For sorting python dictionary using key
#matplotlib.rcParams.update({'font.size': 12, 'family' : 'serif', 'serif':['Times']})
#matplotlib.rcParams.update({'font.size': 10, 'fontname' : 'Courier'})

from collections import defaultdict
import sys

#import InputClass
#from InputClass import *
import re # NEeded for splitting a string with a list of delimiters


class Utility:   
    def __init__(self, arch_file_path, event_map_path, exclude_path):
        self.arch_path = arch_file_path
        self.event_map_path = event_map_path
        self.exclude_path = exclude_path
   
    # This function generates all possible group names and a histogram based on
    # an input correlation file. 
    def generate_all_possible_group_names(self, corr_filename):
        inputObj = InputReader()
        inputObj.set_filename(corr_filename)
        varlist = inputObj.load_only_first_column(corr_filename, True)
        delimit=":|::|,|_|-"
        groupsDict = defaultdict(int)
        for var in varlist:
            var = var.rstrip("\n")
            # generate every single possible substring that can potentially be a group name
            substrList = re.split(delimit, var)
            #print substrList, var
            for substr in substrList:
                if not (substr.isspace() or substr == ''):
                    if substr in groupsDict:
                        groupsDict[substr] += 1 # n+1st occurrence
                    else:
                        groupsDict[substr] = 1 #first occurrence
                    ####### if
                ####### if
            ####### for
        ############## 
        ## Now, generate the "architecture_groups.txt" file
        num_key = 0
        filename = self.arch_path
        f = open(filename, "w")
        for key, val in groupsDict.items():
            if not (key.isspace() or key == ''):
                #print key, val
                f.write(key + "\n")
            num_key += 1
            #print num_key
        f.close()

        ############# Draw histogram
        import pylab as pl
        X = np.arange(0, len(groupsDict))
        fig = pl.figure(1)
        gs = matplotlib.gridspec.GridSpec(1,1)
        ax = fig.add_subplot(gs[0])
        ax.bar(X, groupsDict.values(), align='center', width=0.5)
        ax.set_xticks(X)
        ax.set_xticklabels(groupsDict.keys(), rotation=90, fontsize=5)
        ymax = max(groupsDict.values()) + 1
        ax.set_ylim(0, ymax)
        ax.set_xlim(auto=True)
        ax.tick_params(axis='both', direction='out')
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        plt.axis('tight')	

        outputname = "hist_allPossibleGroups.pdf"
        pp = PdfPages(outputname)
        pp.savefig(fig, transparent=True)
        outputname = "hist_allPossibleGroups.png"
        pl.savefig(outputname, transparent=True)
        pp.close()
    #######################
   
    #for one signle event
    def assign_event_to_eventGroup(self,event_name, group_list):
        #read event_map.txt file and match known event names to the appropiate event group
        found = 0
        delimiter = "=>"
        group_name = []
        ########### STATICGROUPING
        if os.path.exists(self.event_map_path) == True:
            with open(self.event_map_path, 'r') as eventMap:
                for line in eventMap:
                    line = line.rstrip('\n') #get rid of the new line character on the end of each line
                    if (line.partition(delimiter)[0]).lower() == event_name.lower(): #if the file event name equals the specified group name from the parameter
                        group_name_list = (line.partition(delimiter)[2]).split(",") #group name list, is a list of the assigned groups form file
                        found = 1
                        for g in group_name_list:
                            #print event_name, "\t", g
                            group_name.append(g)
                ########## DYNAMIC GROUPING #####$$
                if found == 0:
                    s = event_name.lower()
                    if any(group.lower() in s for group in group_list[0]):
                        group_name = [ group for group in group_list[0] if group.lower() in s] [:]
        ########
        print ("assign_event_to_eventGroup->GROUP NAME: "+ group_name)
        return group_name
    #for a list of events
    def assign_event_list_to_eventGroups(self,event_names, group_list):
        #read event_map.txt file and match known event names to the appropiate event group
        found = 0
        eventMapping = defaultdict(list)
        delimiter = "=>"
        for name in event_names:
            found = 0
            group_name_list = []
            if os.path.exists(self.event_map_path) == True:
                with open(self.event_map_path, 'r') as eventMap:
                    for line in eventMap:
                        line = line.rstrip('\n')
                        if (line.startswith('#')):
                                #print (line, "is a comment")
                                continue
                        if (line.partition(delimiter)[0]).lower() == name.lower():
                            group_name_list = (line.partition(delimiter)[2]).split(",")
                            found = 1
                        elif (line.partition(delimiter)[0]).lower() in name.lower():
                            group_name_list = (line.partition(delimiter)[2]).split(",")
                            found = 1
            #if found == 1:
                #print('STATIC: ', group_name_list, "->", name)
            if found == 0:
                s = name.lower()
                #if any(group.lower() in s for group in group_list):
                    #print (s, "--->", any(group.lower() in s for group in group_list))
                group_name_list = [ group for group in group_list if group.lower() in s] [:]

            if (len(group_name_list) == 0 or len(group_name_list[0]) == 0):
                group_name_list = ['UNDEFINED']
                #print("No group for ", name)
            #Add this event with name "name" to the formulated/found group name
            for group_name in group_name_list:
                eventMapping[group_name].append(name)
        print (eventMapping.items())
        return eventMapping
##gl = group_name in lower case
    def check_if_in_a_dict(self, gl, d):
        x = gl
        flag = 0
        for key, val in d.items():
            if (gl.lower() in key.lower()) or (key.lower() in gl.lower()):
                x = val
                flag = 1
                break
        return x, flag
    
    def check_which_keys_belong_to_my_group(self,gl, d):
        x = gl
        newlist = []
        newlist.append(gl)
        for key, val in d.items():
            print ("check_which_keys_belong_to_my_group: " + key)
            if (gl.lower() in key.lower()) or (key.lower() in gl.lower()):
                newlist.append(val[:])
        return newlist
                
    def assign_x_to_all_variables_in_this_group(self,group_name, event_name_list, col, group_members_dict):
        eventNameList = []
        gl = group_name.lower()
        flag = 0
     
        list_of_group_members = group_members_dict[group_name]
    
        for s in event_name_list:
            is_present = 0
            for group_member in list_of_group_members:#{
                if (group_member.lower() == s.lower()): #then classify this event as belonging to this group
                    eventNameList.append(col)
                    flag += 1
                    is_present = 1
                    break
            #}
            if is_present == 0:
                eventNameList.append('')
        return flag, eventNameList
        
    def get_event_list(self, filename):
        eventlist = []
        with open(filename,'r') as eventlist_file:
            for line in eventlist_file:
                #Each line may be a group of events, derived by multiplex.C
                [eventlist.append(ev) for ev in (line.partition('\n')[0]).split(',')]
        return eventlist
        
    def traverse_dictionary(self,dict):
        for key, val in dict.items():
            print (key + " " + dict[key].values())

    def get_exclude_groups_list(self):
        exclude_groups = []
        #read exclude_groups.txt
        if os.path.exists(self.exclude_path) == True:
            with open(self.exclude_path,'r') as ExGroups:
                for line in ExGroups:
                    exclude_groups.append(line.partition('\n')[0])
        return exclude_groups

    def set_arch_groups(self):
        arch_groups = []
        arch_dict = defaultdict(list)
        new_groups = []
        uncore_flags = {}
        print(self)
        if os.path.exists(self.arch_path) == True:
            with open(self.arch_path,'r') as groups:
                for line in groups:
                    eq = []
                    line = line.strip()
                    mainGroup=line.partition(',:')[0] #first column
                    flag = mainGroup.split(',')[1]
                    mainGroup = mainGroup.split(',')[0]
                    parent = mainGroup.partition("\n")[0] #
                    #print (mainGroup, flag)
                    uncore_flags[mainGroup] = int(flag)
                    if arch_dict.__contains__(parent) == False:
                        if self.is_in_the_dict(arch_dict,parent) == 0:
                            arch_dict[parent].append(parent) #if the group is not already in the dictionary the group is added and is it's own child
                    if line.partition(':')[2] != "": #if there is more data on that line
                        eqg = line.partition(':')[2] #equivelent groups is a list of remaining information on that line
                        eq = eqg.split(",") #put the equivalent groups in a list
                        for group in eq:
                            if arch_dict.__contains__(group):
                                del arch_dict[group] #if any equivalent group is already in the dictionary as a key it will be deleted
                        for key in eq:
                            arch_dict[parent].append(key) #all equivalent groups and the parent group will become the child value
        for key, val in arch_dict.items():
            arch_groups.append(key)
        return arch_groups, uncore_flags, arch_dict

    # Return hspc, rs, cs, fontsize, bott, height
    def get_barchart_parameters(self):
        import os.path
        filename = "config.txt"
        ## Declare default values
        hspc=0.2 # height of the chart
        rs= 5       
        cs = 5
        ## For the single column charts, the the following.
        fs = 3 #fontsize of the chart
        bott = 0.5 ## howmuch space at the bottom of the chart
        height=0.15 ## Height of each cell of the table
        arr = defaultdict(float)
        i = 0
        delimit = "="
        if os.path.isfile(filename):
            with open(filename, 'r') as config:
                for line in config:
                    line = line.rstrip('\n')
                    if line.startswith("#"):
                        print ("Comment")
                    else:
                        pair = re.split(delimit, line)
                        print (pair[0] + " " + pair[1])
                        if isinstance( pair[1], ( int, long ) ):
                            arr[pair[0]] = int(pair[1])
                        else:
                            arr[pair[0]] = float(pair[1])
                        i += 1
        return arr
              
    def multikeysort(items, columns):
        from operator import itemgetter
        comparers = [ ((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in columns]  
        def comparer(left, right):
            for fn, mult in comparers:
                result = cmp(fn(left), fn(right))
                if result:
                    return mult * result
                else:
                    return 0
        return sorted(items, cmp=comparer)
            

    def is_in_the_dict(self, d, val_param):
        flag = 0
        for key, value in d.items():
            if val_param in value[:]:
                flag = 1
        return flag

if __name__ == "__main__":
    obj =  Utility(sys.argv[1], sys.argv[2], sys.argv[3])
    new_groups = []
    arch_dict = defaultdict(list)
    # if "assignSingle" in sys.argv[1]:
    #     obj.assign_event_to_eventGroup("L1P_MISS_L1D_HIT", groups)
    # if "assignList" in sys.argv[1]:
    #     obj.assign_event_list_to_eventGroups(event_names, groups)
    ExGroups=obj.get_exclude_groups_list()
    AGroups, uncore_flags, arch_dict = obj.set_arch_groups()
    eventlist = obj.get_event_list(sys.argv[4])
    eventmap = obj.assign_event_list_to_eventGroups(eventlist, AGroups)
    for key, val in eventmap.items():
        print (key)
        for v in val:
            print ("--", v)
    exclude_event_list = eventmap['UNDEFINED']

    allowed_events = []
    ev_to_res_map = defaultdict()
    try:	
        with open('../resources/filter.txt','r') as fl:
            for line in fl:
                line = line.strip('\n')
                if (line not in exclude_event_list):
                    allowed_events.append(line)
    except IOError:
        print("File does not exist. Pruning eventlist instead.")
        for ev in eventlist:
            if (ev not in exclude_event_list):
                allowed_events.append(ev)
        

    for ev in allowed_events:
        for res, event_list in eventmap.items():
            if ev in event_list:
                ev_to_res_map[ev] = res
    with open('../resources/ascent/ev_to_res_map.csv','w') as csv_file:
        csv_writer = csv.writer(csv_file)
        columns = ['Event']
        for event in allowed_events:
                columns.append(event)
        csv_writer.writerow(columns)

        row = ['Resource']
        for ev, res in ev_to_res_map.items():
                row.append(res)
        csv_writer.writerow(row)
        

    # with open('architecture_groups.txt','r') as groups:
    #     for line in groups:
    #         eq = []
    #         line = line.strip()
    #         Nline=line.partition(':')[0]
    #         new_groups.append(Nline.partition("\n")[0])
    #         parent = Nline.partition("\n")[0]
    #         if arch_dict.__contains__(parent) == False:
    #             if obj.is_in_the_dict(arch_dict, parent) == 0:
    #                 print ("Adding parent: " + parent)
    #                 arch_dict[parent].append(parent)
    #         if line.partition(':')[2] != "":
    #             eqg = line.partition(':')[2]
    #             eq = eqg.split(",") 
    #             for group in eq:
    #                 if arch_dict.__contains__(group):
    #                     del arch_dict[group]
    #             for key in eq:
    #                 arch_dict[parent].append(key)
    # for group, members in  arch_dict.items():
    #     print (group, members)
    ########### Testing out generation of all possible groups and a histogram
    
    #obj.generate_all_possible_group_names(sys.argv[1])
    #obj.get_barchart_parameters()




def test(data_loader):
    # All data are in dictionaries
    # First key is always region, always returns a dictionary
    # Second key depends on the data, either is a resource name or event name
    # This module should be scheduled below "compute_rsm_task_all_regions"
    # and force_process should be set to "false". 
    rsm_results = data_loader.get_option('rsm_results')
    rsm_res_errors = data_loader.get_option('rsm_res_errors')
    rsm_ev_errors = data_loader.get_option('rsm_ev_errors')
    rsm_alphas = data_loader.get_option('rsm_alphas')
    rsm_norm_data = data_loader.get_option('rsm_norm_data')


    for region in rsm_results:
        print("Region: ", region)
        for resource in rsm_results[region]:
            print("%s=%s" % (resource, rsm_results[region][resource]))

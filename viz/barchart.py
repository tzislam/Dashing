import sys
import numpy as np
import pandas
import plotly.graph_objects as go
import csv
from numpy import nan

colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
	'#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
	'#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
	'#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']

def load_imbalance(data_loader):
	proc_configs = data_loader.proc_configs
	for reg in data_loader.regions:	
		for ev in data_loader.events:
			ev_importance = importance(data_loader['name'], reg, ev)
			if ev_importance <= 0.005:
				continue
			
			proc_vals_across_configs = find_proc_vals_across_configs(data_loader, proc_configs, reg, ev)

			fig = go.Figure()
			for proc_i, vals_per_proc in enumerate(proc_vals_across_configs):
				fig.add_trace(go.Bar(
					name = proc_i,
					x = proc_configs,
					y = vals_per_proc))

			fig.update_layout(autosize=True, title="%s, %s"%(reg,ev), barmode="stack")
			fig.layout.xaxis.title = "Number of Processes"
			fig.layout.xaxis.tickvals = proc_configs
			fig.layout.yaxis.title = "Raw values per process"
			data_loader['charts'].append(fig)
			break
		break



def normalize_to_sum_to_1(proc_vals):
	the_sum = sum(proc_vals)
	if the_sum == 0: return proc_vals
	return [d/the_sum for d in proc_vals]
		

#returns nxm matrix where n=largest process count(32 for haswell, 68 for knl), m = number of configs 
def find_proc_vals_across_configs(data_loader, proc_configs, reg, ev):
	proc_vals_across_configs = np.zeros((proc_configs[-1], len(proc_configs)))

	for config_i, config in enumerate(proc_configs):
		config_data = data_loader.raw_h5_map[reg][ev][config_i]
		config_data = normalize_to_sum_to_1(config_data)

		for dp_i, datapoint in enumerate(config_data):
			proc_vals_across_configs[dp_i][config_i] = datapoint
		

	return proc_vals_across_configs


#def standardize_length(config_data, length):
#	standardized_array = np.zeros(length)
#	for i in range(len(config_data)):
#		standardized_array[i] = config_data[i]
#	return standardized_array
		


def create_barchart(data_loader):
    
    name = data_loader.get_option('name', 'untitled barchart')
    rsm_results = data_loader['rsm_res_errors']
    regions = [key for key in rsm_results]
    resources = [resource for key in regions for resource in rsm_results[key]]
    resources = list(set(resources))

    resources = sorted(resources)
    data = np.zeros((len(regions), len(resources)))
    for i, region in enumerate(regions):
        for j, resource in enumerate(resources):
            data[i, j] = rsm_results[region][resource]
    
    for i in range(len(resources)):
        if resources[i] == 'UNDEFINED':
            resources[i] = 'UNDEF'
        if resources[i] == 'OFFCORE':
            resources[i] = 'OFF'

    x_font_dict = {
        'rotation': 90,
        'fontweight': 'semibold'
    }

    title_font_dict = {
        'fontweight': 'bold',
        'fontsize': 18
    }

    bar_graphs = []

    title_str = "%s | %s"
    raw_data = []
    for reg_i, region in enumerate(regions):
        #print(region)
        valid_indices = []
        reg_resources = []
        for i in range(len(resources)):
            if np.isnan(data[reg_i, i]):
                pass
                #print("Removing ", resources[i])
            else:
                valid_indices.append(i)
                reg_resources.append(resources[i])
        
        raw_data.append(data[reg_i, valid_indices])

    for i, norm_data in enumerate(normalize(raw_data)):
        bar_graphs.append(go.Bar(
            x=reg_resources,
            y=norm_data,
            name=regions[i]))
     

    fig = go.Figure(bar_graphs)
    fig.update_layout(title=name, autosize=True)
    fig.layout.xaxis.title="resource"
    fig.layout.yaxis.title="rsm score"

    data_loader['charts'].append(fig)


def create_rsm_percent_barchart(data_loader):
    rsm_results = data_loader['rsm_res_errors']
    regions = data_loader.get_regions()
    resources = [resource for key in regions for resource in rsm_results[key]]
    resources = sorted(list(set(resources)))

    percent_dict = {}
    for reg in regions:
        percent_dict[reg] = {}
        eff_loss = data_loader.get_app_eff_loss(reg)
        base_error = np.linalg.norm(eff_loss)
        for res in resources:
            if np.isnan(rsm_results[reg][res]):
                percent_dict[reg][res] = np.nan
            else:
                reduction = base_error - rsm_results[reg][res]
                percent_dict[reg][res] =  (reduction / base_error) * 100.0
    
    data = np.zeros((len(regions), len(resources)))
    for i, reg in enumerate(regions):
        for j, res in enumerate(resources):
            data[i, j] = percent_dict[reg][res]
    
    for i in range(len(resources)):
        if resources[i] == 'UNDEFINED':
            resources[i] = 'UNDEF'
        if resources[i] == 'OFFCORE':
            resources[i] = 'OFF'
    
    bar_graphs = []
    for res_i, resource in enumerate(resources):
        res_data = data[:, res_i]

        if np.all(np.isnan(res_data)):
            print("Skiping %s for having nan values..." % resource)
            continue
        
        hover_labels = []
        hover_text = 'Region: %s<br>Resource: %s<br>Percent Error Reduced: %0.2f%%<br>'
        for i in range(len(regions)):
            hover_labels.append(hover_text % (regions[i], resource, res_data[i]))
        
        bar_graphs.append(go.Bar(
            name=resource,
            x=regions,
            y=res_data,
            hovertext=hover_labels,
            hoverinfo="text",
            marker_color=data_loader.get_resource_color(resource)))
    
    fig = go.Figure(bar_graphs)
    fig.update_layout(autosize=True)
    fig.layout.xaxis.title = "Region"
    fig.layout.yaxis.title = "Percent Accuracy"
    fig.update_yaxes(range=[0.0, 100.0])
    data_loader['charts'].append(fig)

def create_rsm_error_barchart(data_loader):
    rsm_results = data_loader['rsm_results']
    regions = [key for key in rsm_results]
    resources = [resource for key in regions for resource in rsm_results[key]]
    resources = sorted(list(set(resources)))
    
    data = np.zeros((len(regions), len(resources)))
    for i, reg in enumerate(regions):
        for j, res in enumerate(resources):
            data[i, j] = rsm_results[reg][res]
    
    for i in range(len(resources)):
        if resources[i] == 'UNDEFINED':
            resources[i] = 'UNDEF'
        if resources[i] == 'OFFCORE':
            resources[i] = 'OFF'
    
    bar_graphs = []
    for res_i, resource in enumerate(resources):
        res_data = data[:, res_i]

        if np.all(np.isnan(res_data)):
            print("Skiping %s for having nan values..." % resource)
            continue
        
        bar_graphs.append(go.Bar(
            name=resource,
            x=regions,
            y=res_data))
    
    fig = go.Figure(bar_graphs)
    fig.update_layout(autosize=True)
    fig.layout.xaxis.title = "Region"
    fig.layout.yaxis.title = "RSM Score"
    fig.update_yaxes(range=[0.0, 1.0])
    data_loader['charts'].append(fig)
    




def create_barchart_2(data_loader):
    
    name = data_loader.get_option('name', 'untitled barchart')
    rsm_results = data_loader['rsm_res_errors']
    regions = [key for key in rsm_results]
    resources = [resource for key in regions for resource in rsm_results[key]]
    resources = list(set(resources))

    resources = sorted(resources)
    data = np.zeros((len(resources), len(regions)))
    for i, resource in enumerate(resources):
        for j, region in enumerate(regions):
            data[i, j] = rsm_results[region][resource]
    
    for i in range(len(resources)):
        if resources[i] == 'UNDEFINED':
            resources[i] = 'UNDEF'
        if resources[i] == 'OFFCORE':
            resources[i] = 'OFF'
    
    # Remove () and :: from names
    for i in range(len(regions)):
        if ':' in regions[i]:
            regions[i] = regions[i].split(':')[-1]
        
        if '()' in regions[i]:
            regions[i] = regions[i].split('()')[0]

    x_font_dict = {
        'rotation': 90,
        'fontweight': 'semibold'
    }

    title_font_dict = {
        'fontweight': 'bold',
        'fontsize': 18
    }

    bar_graphs = []

    title_str = "%s | %s"
    raw_data = []
    for res_i, resource in enumerate(resources):
        #print(region)
        valid_indices = []
        reg_resources = []
        for i in range(len(regions)):
            if np.isnan(data[res_i, i]):
                pass
                #print("Removing ", resources[i])
            else:
                valid_indices.append(i)
                reg_resources.append(regions[i])
        
        raw_data.append(data[res_i, valid_indices])

    for i, norm_data in enumerate(normalize(raw_data)):
        bar_graphs.append(go.Bar(
            x=reg_resources,
            y=norm_data,
            name=resources[i]))
     

    fig = go.Figure(bar_graphs)
    fig.update_layout(title=name, autosize=True)
    fig.layout.xaxis.title="Resource"
    fig.layout.yaxis.title="RSM"

    data_loader['charts'].append(fig)



def calc_color(data_loader, event):
	res = data_loader.ev_to_res_map[event][0]
	return colors[hash(res) % len(colors)]


def importance(name, region, event):
	with open('ev_belief_perc.csv', 'r') as csvfile:
		csv_reader = csv.reader(csvfile,delimiter=',')
		for row in csv_reader:
			if row[0].strip() == name.strip() and \
				row[1].strip() == region.strip() and \
				row[3].strip() == event.strip():
				return float(row[4])
		else:
			return 0.0
	

#source: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

#assuming that scores are either all nan, or have no nan's in them
def remove_nan(df,resources):
	valid_data = []
	for resource in resources:
		if not np.isnan(df[resource][0]):
			valid_data.append(resource)
	return valid_data


def normalize_1d(data):
	min_val = min(data)
	max_val = max(data)
	return [ (d-min_val)/(max_val-min_val) for d in data ]



#bad implementation, fix later
def normalize(data):
	norm_bars = []
	min_val = find_min(data)
	max_val = find_max(data)
	for bargraph_data in data:
		norm_data = []
		for x in bargraph_data:
			norm_data.append( (x-min_val)/(max_val-min_val) )
		norm_bars.append(norm_data)

	return norm_bars

def find_min(data):
	min_val = 9999999.9
	for bargraph_data in data:
		for x in bargraph_data:
			if x < min_val:
				min_val = x
	
	return min_val

def find_max(data):
	max_val = 0.0
	for bargraph_data in data:
		for x in bargraph_data:
			if x > max_val:
				max_val = x

	return max_val

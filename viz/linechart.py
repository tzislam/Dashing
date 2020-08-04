import csv
import numpy as np
import pandas
import os
import plotly.tools as tls
import plotly.graph_objects as go


def raw_values_per_proc_config(data_loader):
	proc_configs = data_loader.proc_configs
	h5_map = data_loader.h5_map
	rsm_results = data_loader['rsm_results']
	resources = set()
	for reg in rsm_results:
		for res in rsm_results[reg]:
			resources.add(res)
	resources = sorted(list(resources))

	save_figure = data_loader.get_option('save_raw_line', False)
	show_title = data_loader.get_option('show_raw_line_title', True)

	for reg in data_loader.regions:
		fig = go.Figure()
		fig.add_trace(go.Scatter(
			name = "Efficiency Loss",
			x = proc_configs,
			y = data_loader.get_app_eff_loss(reg),
			legendgroup="!!!",
			line=dict(color="black", width=4)))
	
		for ev in data_loader.get_events():
			ev_importance = importance(data_loader['name'], reg, ev)
			if ev_importance <= 0.005:
				continue

			data_per_proc = []
			for proc_i, proc in enumerate(proc_configs):
				data_per_proc.append(h5_map[reg][ev][proc_i][0])
			
			res = data_loader.ev_to_res_map[ev][0]
			ev_color = data_loader.get_resource_color(res)

			fig.add_trace(go.Scatter(
				name = ev,
				x = proc_configs,
				y = normalize_1d(data_per_proc),
				legendgroup=ev_color,
				line=dict(color=ev_color, width=2)))
		
		title_name = reg if show_title else ''
		fig.update_layout(autosize=True, title=title_name)
		fig.layout.xaxis.title = "Number of Processes"
		fig.layout.xaxis.tickvals = proc_configs
		fig.layout.yaxis.title = "Normalized Event Count"
		fig.update_layout(	font={'size': 10})

		data_loader['charts'].append(fig)

		if save_figure:
			region_filename = reg.replace(':', '_')
			region_filename = region_filename.replace(' ', '_')
			file_path = '%s_%s.pdf' \
				% (data_loader.get_config_name(), region_filename)

			dir_path = os.path.join('viz_output', 'raw_line')
			if not os.path.exists(dir_path):
				os.makedirs(dir_path)
			
			file_path = os.path.join(dir_path, file_path)
			fig.write_image(file_path, width=1000, height=500)


def calc_color(data_loader, event,res_color_map ):
	res = data_loader.ev_to_res_map[event][0]
	if res == "ATOMIC":
		return "#1F77B3"
	elif res == "STALL":
		return "#D62628"
	elif res == "TLB":
		return "#FF9795"
	elif res == "FE":
		return "#FFBA77"
	elif res == "MEM":
		return "#41149C"
	else:
		return res_color_map[res]
		
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




#def effloss_vs_counter_val(data_loader):
#    
#	all_procs = [1, 4, 8, 12, 16, 20, 24, 28, 32]
#
#	#note to future me: dont use this method
#	#instead, stuff all the graphs into one figure
#	#using subplot() or something
#	figures_across_regions = {}
#
#	for region in data_loader.get_regions():
		  #		print("\n--------------")
#		print("Region: ", region)
#		
#		# Remove () and :: from names
#		region = region.split(':')[-1]
#		region = region.split('()')[0]
#		
#		#can this be moved outside the loop?
#		app_data = data_loader.get_app_data(region)	
#		eff_loss = data_loader.get_app_runtime(region)
#
#		fig = plt.figure()
#		ax = fig.add_subplot(111)
#		
#		figures_across_counters = []
#
#		#for each counter
#		for i in range(len(app_data[0])):
#			print("Generating plot for counter: ", data_loader.get_events()[i])
#
#			#plot data
#			counter_vals = app_data[:,i]
#			ax.plot(np.arange(len(eff_loss)), eff_loss)
#			ax.plot(np.arange(len(counter_vals)), counter_vals)
#			##########
#
#			#make graph prettier
#			plt.title(region + "." + data_loader.get_events()[i])
#			ax.set_ylim([0,1.05])		
#			padding = len(procs) - len(all_procs)
#			labels = []
#			for _ in range(padding):
#				labels.append('')
#			[labels.append(proc) for proc in procs]
#			plt.xticks(np.arange(len(procs)), labels)
#			####################			
#
#			plotly_fig = tls.mpl_to_plotly(fig)
#			plotly_fig['layout']['showlegend'] = True
#			figures_across_counters.append(plotly_fig)
#			
#		figures_across_regions[region] = (figures_across_counters)
#
#	if 'charts' not in data_loader.options:
#		data_loader.options['charts'] = {}
#	data_loader.options['charts']["linechart"] = figures_across_regions



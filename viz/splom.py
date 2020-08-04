# SPLOM = scatter plot matrix





# NOTE: not done. just for reference





import sys
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_splom(csvFilePath):
	df = pd.read_csv(csvFilePath)

	resources = df.columns[1:]
	regions = list(df.values[:, 0])
	data = df.values[:, 1:].astype(float)
	
	
	# Flip regions around for readability
	regions = regions[::-1]
	data[:,:] = data[::-1, :]
	
	# Remove () and :: from names
	for i in range(len(regions)):
	    if ':' in regions[i]:
	        regions[i] = regions[i].split(':')[-1]
	    
	    if '()' in regions[i]:
	        regions[i] = regions[i].split('()')[0]
	
	# Sort resources for readability
	resources = resources.values
	resource_indices = np.argsort(resources)
	resources[:] = resources[resource_indices]
	data[:,:] = data[:, resource_indices]

	index_vals = regions.astype('category').cat.codes #colors based on this
	marker = dict(color=index_vals,
	              showscale=False, # colors encode categorical variables
	              line_color='white', line_width=0.5)

	dimensions = []
	for reg in regions:
		dimensions.append(dict(label=region, values=df[region]))

	data = go.Splom(dimensions=dimensions, text=regions, marker=marker)
	fig = go.Figure(data)
	
	
	fig.update_layout(
	    title='test title',
	    width=600,
	    height=600,
	)
	
	fig.show()

if __name__ == "__main__":
	create_splom(sys.argv[1])

import sys
import numpy as np
import os
import pandas
#import plotly.tools as tls
import plotly.graph_objects as go

def create_heatmap(data_loader):
    name = data_loader.get_option('name', 'untitled heatmap')
    save_heatmap = data_loader.get_option('save_heatmap', False)
    rsm_results = data_loader['rsm_results']
    regions = data_loader.get_regions()[::-1]
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
    
    valid_indices = []
    valid_resources = []
    for resource_index, resource in enumerate(resources):

        # we grab the first value to check if its nan
        # if any value is nan, all must be nan
        # so its safe to check only the first value
        if np.isnan(data[0, resource_index]):
            print("Removing ", resource)
        else:
            valid_indices.append(resource_index)
            valid_resources.append(resource)

    data *= 100.0

    fig = go.Figure(data=go.Heatmap(
        x = valid_resources,
        y = regions,
        z = data[:, valid_indices],
        type = 'heatmap',
        colorbar={"title": "RSM Score"},
        zmin=0.0,
        zmax=100.0,
        colorscale = [
            [0.0, 'rgb(255,255,255)'],
            [0.1, 'rgb(255,255,204)'],
            [0.2, 'rgb(255,237,160)'],
            [0.3, 'rgb(254,217,118)'],
            [0.4, 'rgb(254,178,76)'],
            [0.5, 'rgb(253,141,60)'],
            [0.6, 'rgb(252,78,43)'],
            [0.7, 'rgb(227,26,28)'],
            [0.8, 'rgb(189,0,38)'],
            [0.9, 'rgb(128,0,38)'],
            [1.0, 'rgb(80,0,12)']]
    ))

    # an attempt to force the tiles to be squares
    #fig.layout.update(title=title, autosize=False,
    #     scene=dict(
    #        aspectmode='manual',
    #        aspectratio=go.layout.scene.Aspectratio(
    #           x=700, y=int((700/len(valid_resources)+1)*len(regions)))
    #        ))
    fig.layout.update(title=name, autosize=False, height=700, width=700)
    fig.layout.xaxis.title="Resource"
    fig.layout.yaxis.title="Region"
    fig.update_xaxes(tickangle=-90)
    data_loader['charts'].append(fig)

    
    if save_heatmap:
        file_path = '%s.pdf' % data_loader.get_config_name()
        dir_path = os.path.join('viz_output', 'heatmap')

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        file_path = os.path.join(dir_path, file_path)
        fig.write_image(file_path)

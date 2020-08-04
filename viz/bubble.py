from collections import defaultdict

import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot, plot
from plotly.subplots import make_subplots


def load_and_reshape_data(data_loader):
    # data_loader options
    n = data_loader.get_option('bubble_n', 10)
    res_map = data_loader.ev_to_res_map

    # Get rsm errors and variables from data_loader
    rsm_errors = data_loader['rsm_ev_errors']
    regions = [key for key in rsm_errors]
    events = [ev for key in regions for ev in rsm_errors[key]]
    events = list(set(events))
    
    # We reshape our data by having the columns event, resource, reg1, reg2, ...
    reshaped_data = []
    for ev in events:
        if len(res_map[ev]) != 1:
            print("WARNING: %s has multiple regions: %s" % (ev, res_map[ev]))

        row = [ev, res_map[ev][0]]
        for reg in regions:
            row.append(rsm_errors[reg][ev])
        
        reshaped_data.append(row)
    
    header = ['Event', 'Res']
    for reg in regions:
        header.append(reg)
    
    df = pd.DataFrame(reshaped_data, columns=header)

    return df, regions, n



def bubble(data_loader):

    df, regions, n = load_and_reshape_data(data_loader)

    for reg in regions:
        # Get the top and bottom n values of this region
        top_subset = df.nlargest(n, reg)
        bot_subset = df.nsmallest(n, reg)
        subset = pd.concat((top_subset, bot_subset))

        # Create our figure
        fig = px.scatter(subset, x="Event", y=reg,
            size=reg, color="Res", log_x=False,
            size_max=5, color_discrete_sequence= px.colors.sequential.Plasma[-2::-1])
        fig.update_traces(textposition='top center')

        fig.update_layout(
            height=800,
            title_text='Error in prediction')
        
        data_loader['charts'].append(fig)


         
def bubble_all_regions(data_loader):
    df, regions, n = load_and_reshape_data(data_loader)
    top_subset = df.nlargest(n, regions)
    bot_subset = df.nsmallest(n, regions)
    subset = pd.concat((top_subset, bot_subset))

    fig = px.scatter(subset, x="Event", y=regions,
            size=regions, color="Res", facet_col=regions,
            log_x=False, size_max=5, color_discrete_sequence= px.colors.sequential.Plasma[-2::-1])
    fig.show()
    fig.update_traces(textposition='top center')

    fig.update_layout(
        height=800,
        title_text='Error in prediction')

    
def scatter_matrix(data_loader):
    df, regions, n = load_and_reshape_data(data_loader)
    top_subset = df.nlargest(n, regions)
    bot_subset = df.nsmallest(n, regions)
    subset = pd.concat((top_subset, bot_subset))

    fig = px.scatter_matrix(subset)
    fig.show()



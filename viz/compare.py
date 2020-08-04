import sys
import numpy as np
import os
import pandas
import plotly.graph_objects as go


def compare_apps(data_loader_dict): # data_loader_dict = {config_name: data_loader, ...}

	fig = go.Figure()
	for config, dl in enumerate(data_loader_dict)
		rsm_results = data_loader['rsm_results']
		title = data_loader['title']

		fig.add_trace(go.Scatter(

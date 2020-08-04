
import numpy as np
import plotly.graph_objects as go
import os

def create_runtime_comparison(data_loaders, global_options):
    pairs = global_options['runtime_pairs']

    for pair in pairs:
        app_pair1, app_pair2 = pair.split(',')
        app1, reg1 = app_pair1.split(':', 1)
        app2, reg2 = app_pair2.split(':', 1)
        create_runtime_linechart(data_loaders, app1, app2, reg1, reg2)


def create_runtime_linechart(data_loaders, app1, app2, reg1, reg2):
    dl1 = data_loaders[app1]
    dl2 = data_loaders[app2]
    y_axis1 = dl1.get_app_runtime(reg1, rescale=False)
    y_axis2 = dl2.get_app_runtime(reg2, rescale=False)
    x_axis = dl1.proc_configs

    y_axis1 = np.multiply(y_axis1, x_axis)
    y_axis2 = np.multiply(y_axis2, x_axis)

    scatter_plot1 = go.Scatter(x=x_axis, y=y_axis1, name=app1)
    scatter_plot2 = go.Scatter(x=x_axis, y=y_axis2, name=app2)

    fig = go.Figure()
    fig.add_trace(scatter_plot1)
    fig.add_trace(scatter_plot2)
    title_str = '%s-%s vs. %s-%s' % (app1, reg1, app2, reg2)
    fig.update_layout(title=title_str)

    fig.layout.xaxis.title = "Processor Configurations"
    fig.layout.yaxis.title = "Runtime"
    fig.update_xaxes(title_font=dict(size=18))
    fig.update_yaxes(title_font=dict(size=18))

    fig.show()

    dl1['charts'].append(fig)
    dl2['charts'].append(fig)

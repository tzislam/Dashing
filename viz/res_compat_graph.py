
import numpy as np
import plotly.graph_objects as go
import os

def create_res_versus_compat_graph(data_loaders, global_options):
    save_compat = global_options['save_compat'] \
        if 'save_compat' in global_options else False
    compat_show_labels = global_options['compat_labels'] \
        if 'compat_labels' in global_options else True
    compat_show_figure = global_options['compat_show_fig'] \
        if 'compat_show_fig' in global_options else False
    compat_show_axis_labels = global_options['compat_show_titles'] \
        if 'compat_show_titles' in global_options else False

    for dl_name, dl in data_loaders.items():
        if 'compat_results' not in dl:
            print("Not in %s" % dl_name)
            continue
        
        for key in dl['compat_results']:
            generate_linechart(key, data_loaders, dl_name, save_compat,
                compat_show_labels, compat_show_figure, compat_show_axis_labels)
            print("Assigning a chart to %s" % dl_name)


def generate_linechart(compat_key, data_loaders, dl_name, save_compat,
        compat_show_labels, compat_show_fig, compat_show_axis_labels):
    key_reg1, key_reg2 = compat_key.split(',')
    dl1_name, reg1 = key_reg1.split(':', 1)
    dl2_name, reg2 = key_reg2.split(':', 1)
    print(dl1_name, dl2_name, reg1, reg2)
    
    dl_names = [dl1_name, dl2_name]
    regions = [reg1, reg2]
    dl_pair = [data_loaders[dl1_name], data_loaders[dl2_name]]

    clean_dl_names = []
    for i, dl in enumerate(dl_pair):
        if 'name' in dl:
            clean_dl_names.append(dl['name'])
        else:
            clean_dl_names.append(dl_names[i])
    
    clean_reg_names = list(regions)
    # for i in range(2):
    #     if ':' in regions[i]:
    #         clean_reg_names[i] = clean_reg_names[i].split(':')[-1]
        
    #         clean_reg_names[i] = clean_reg_names[i].split('()')[0]

    title_str = '%s-%s versus. %s-%s'
    save_str = '%s_%s_%s_%s.pdf'
    if dl_names[0] == dl_name:
        title_str %= (dl_names[0], clean_reg_names[0], dl_names[1], clean_reg_names[1])
        save_str %= (dl_names[0], clean_reg_names[0], dl_names[1], clean_reg_names[1])
    else:
        title_str %= (dl_names[1], clean_reg_names[1], dl_names[0], clean_reg_names[0])
        save_str %= (dl_names[1], clean_reg_names[1], dl_names[0], clean_reg_names[0])


    
    compat_score = dl_pair[0]['compat_results'][compat_key]
    resources = [res for res in compat_score if not np.isnan(compat_score[res])]
    resources = sorted(resources)
    res_score = data_loaders[dl_name]['rsm_results']
    res_score = res_score[reg1] if reg1 in res_score else res_score[reg2]

    text_resources = list(resources)
    for i in range(len(text_resources)):
        if text_resources[i] == 'UNDEFINED':
            text_resources[i] = 'UNDEF'
        if text_resources[i] == 'OFFCORE':
            text_resources[i] = 'OFF'
    
    x_axis = [res_score[res] for res in resources]
    y_axis = [compat_score[res] for res in resources]

    y_axis = np.array(y_axis)
    y_axis = np.exp(y_axis)

    val_min = min(y_axis)
    val_max = max(y_axis)
    if not np.isclose(val_min, val_max):
        y_axis = (y_axis - val_min) / (val_max - val_min)
    

    text_labels, text_positions = \
        calculate_text_annotations(x_axis, y_axis, text_resources)

    if not compat_show_labels:
        text_labels = ''
    
    hover_text = ['(%0.3f, %0.3f)<br>%s' % (x_axis[i], y_axis[i], text_resources[i]) \
        for i in range(len(x_axis))]

    scatter_plot = go.Scatter(x=x_axis, y=y_axis, mode='markers+text', text=text_labels,
        textposition=text_positions, hovertext=hover_text, hoverinfo='text')
    fig = go.Figure(scatter_plot)
    fig.update_layout(title=title_str)
    if compat_show_axis_labels:
        fig.layout.xaxis.title = "<b>Resource Significance Measure<br>"
        fig.layout.yaxis.title = "<b>Compatibility Score<br>"
        fig.update_xaxes(title_font=dict(size=18))
        fig.update_yaxes(title_font=dict(size=18))

    line_format = {
        'color': 'red',
        'width': 2,
        'dash': 'dot'
    }

    fig.update_yaxes(range=[-0.1, 1.1])
    fig.update_xaxes(range=[-0.1, 1.1])
    
    shape_1 = go.layout.Shape(
        type='line', x0=-1.0, x1=2.0, y0=0.8, y1=0.8, line=line_format)
    shape_2 = go.layout.Shape(
        type='line', x0=0.8, x1=0.8, y0=-1.0, y1=2.0, line=line_format)
    fig.update_layout(shapes=[shape_1, shape_2])

    data_loaders[dl_name]['charts'].append(fig)

    if save_compat:
        if compat_show_labels:
            dir_path = os.path.join('viz_output', 'compat_graphs')
        else:
            dir_path = os.path.join('viz_output', 'compat_no_labels')

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        file_path = os.path.join(dir_path, save_str)
        fig.write_image(file_path)    

    if compat_show_fig:
        fig.show(config={'editable': True})

def calculate_text_annotations(x_axis, y_axis, text_resources):
    n = len(x_axis)
    points = [np.array((x_axis[i], y_axis[i])) for i in range(n)]
    text_positions = ['top right'] * n
    text_labels = [None] * n
    DISTANCE_CUTOFF = 0.04

    for i in range(n):
        if text_labels[i] is not None:
            continue

        dist_arr = np.zeros(n)
        # We don't calculate for anything behind us
        for j in range(i):
            dist_arr[j] = np.inf
        
        # Calculate distance to all other points
        for j in range(i+1,n):
            dist_arr[j] = np.linalg.norm(points[j] - points[i])

        # Sort into ascending order
        sorted_indices = dist_arr.argsort()
        labels = []
        for dist_index in sorted_indices:
            # We break if the next point is too far (and thus all future points)
            if dist_arr[dist_index] >= DISTANCE_CUTOFF:
                break
            
            labels.append(text_resources[dist_index])
            text_labels[dist_index] = ''

        text_labels[i] = '<b>%s<b>' % (', '.join(sorted(labels)))

    return text_labels, text_positions

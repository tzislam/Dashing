
import numpy as np
import plotly.graph_objects as go

def compat_barchart(data_loaders, global_options):
    
    for dl_name, dl in data_loaders.items():
        if 'compat_results' not in dl:
            print("Not in %s" % dl_name)
            continue
        
        for key in dl['compat_results']:
            generate_barchart(key, dl['compat_results'][key], data_loaders)
            print("Assigning a chart to %s" % dl_name)

def generate_barchart(compat_key, results, data_loaders):
    key_reg1, key_reg2 = compat_key.split(',')
    dl1_name, reg1 = key_reg1.split(':', 1)
    dl2_name, reg2 = key_reg2.split(':', 1)

    print('++++++++++++++++++generate_barchart', key_reg1, key_reg2)
    # Get readable names
    # if 'name' in data_loaders[dl1_name]:
    #     clean_dl1_name = data_loaders[dl1_name]['name']
    # else:
    #     clean_dl1_name = dl1_name
    # if 'name' in data_loaders[dl2_name]:
    #     clean_dl2_name = data_loaders[dl2_name]['name']
    # else:
    #     clean_dl2_name = dl2_name
    clean_dl1_name = key_reg1
    clean_dl2_name = key_reg2

    #reg1 = reg1.split(':')[-1] if ':' in reg1 else reg1
    #reg2 = reg2.split(':')[-1] if ':' in reg2 else reg2
    
    title = '%s (%s) vs. %s (%s)' % (reg1, clean_dl1_name, reg2, clean_dl2_name)

    resources = [key for key in results if not np.isnan(results[key])]
    values = [results[key] for key in resources]

    hover_text = [('Raw Score: %0.3f' % val) for val in values]

    values = np.array(values)
    values = np.exp(values)

    val_min = min(values)
    val_max = max(values)
    if not np.isclose(val_min, val_max):
        values = (values - val_min) / (val_max - val_min)

    for i in range(len(resources)):
        if resources[i] == 'UNDEFINED':
            resources[i] = 'UNDEF'
        if resources[i] == 'OFFCORE':
            resources[i] = 'OFF'

    bar_graph = go.Bar(x=resources, y=values, hovertext=hover_text)
    fig = go.Figure(bar_graph)
    fig.update_layout(title=title, autosize=True)

    data_loaders[dl1_name]['charts'].append(fig)
    data_loaders[dl2_name]['charts'].append(fig)

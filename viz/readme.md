* 1: once finished writing the function that generates the plot, assemble every figure generated into the following structure:
** a dict of of lists, mapping a region_name to a list of figures. Each figure corresponds to a counter, and is a plotly.Figure object.

* 2: add this at the end:
<code>
if 'charts' not in data_loader.options:
    data_loader.options['charts'] = {}
data_loader.options['charts'][chart_name] = list_of_all_figures_this_function_generated
</code>

where chart_name is the style of chart this is (eg: linechart, bubble, heatmap)
and it's value in the dictionary is the list of every figure (plotly.Figure object) generated.



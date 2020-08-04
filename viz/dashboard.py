
import numpy as np
import plotly.offline as py
import dash
import dash_core_components as dcc
import dash_html_components as html
import sys
import webbrowser
import threading
import time


def dashboard_init(data_loaders, global_options):
	webpages = {}
	for app_name, data_loader in data_loaders.items():
		if data_loader.options['charts']:
			webpages[app_name] = create_page(data_loader)
#			for fig in data_loader.options['charts']:
#				fig.write_image("images/%s.pdf" % app_name)
	
	port = global_options['port'] if 'port' in global_options else 7050 

	if len(webpages.keys()) > 0:
		start_server(webpages, port)

# creates a div element that represents a whole webpage
# containing all visualizations for an app
def create_page(data_loader):

	charts = data_loader["charts"]
	title = data_loader.get_option('title', 'untitled chart')
	chart_elems = list(html.H1(children=title))
	for chart in charts:
		chart_elems.append(html.Div(dcc.Graph(id=str(chart), figure=chart)))

	return html.Div(children=chart_elems)


def start_server(webpages, port):

	external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
	index_app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

	# nav bar
	nav_divs = []
	for page in webpages:
		nav_divs.append(html.Li(dcc.Link(page, href='/'+page)))
	nav = html.Ul(children = nav_divs, className="navbar")
	
	# home page
	index_divs = [dcc.Location(id='url', refresh=False)]
	index_divs.append(nav)
	index_divs.append(html.Div(id='page-content'))
	index_app.layout = html.Div(index_divs)
	

	# mimics having different webpages depending on the URL
	@index_app.callback(dash.dependencies.Output('page-content', 'children'),
	[dash.dependencies.Input('url', 'pathname')])
	def display_page(pathname):
		if pathname is None: return
		key = pathname[1:]	
		if key in webpages:
			return webpages[key]
		else:
			return



	app_thread = threading.Thread(target=index_app.run_server,
		kwargs={'debug':True, 'port':port, 'use_reloader':False})
	#index_app.run_server(debug=True, port=port, use_reloader=False)
	app_thread.start()
	webbrowser.open(f'http://127.0.0.1:{port}')




#shelved

#	#search for events/resources/regions, highlight those divs?
#	@index_app.callback(
#		dash.dependencies.Output('placeholder', 'children'),
#		[dash.dependencies.Input('searchbar', 'value')])
#	def search(value):
#		print("searching for: ", value)
#		pagecontent = index_divs[2]
#		print(pagecontent)
		
	

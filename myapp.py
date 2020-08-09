import pandas as pd
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
import plotly.express as px
from dash.dependencies import Input, Output, State

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_gif_component as gif

from datetime import date 
from datetime import datetime
from datetime import timedelta

import math
import locale

from apps import scheduler, utility, alert, covid_curve, test_positivity, death_rate, test_efficiency, fatality

app = dash.Dash(__name__,title="Covid in India",external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

#to get csv data
data_set = scheduler.get_data()
state_code_list = utility.get_state_code_list(data_set)

def get_current_status_card(data_set):
    daily_data = alert.get_daily_data(data_set)
    card_content_confirmed = [
            html.Div(
                [	html.H6("Confirmed",className="text-center"),
                    html.Div(
                        "{0:n}".format(daily_data["Daily Confirmed"].values[0]),
                        className="card-text text-center",
                    ),
                ],className="w-30",style={"background-color":"#ffd6cc","border-radius": "10px",
                						 "box-shadow": "2px 2px 2px lightgrey"}
            )
        ]
    card_content_recovered = [
            html.Div(
                [
                	html.H6("Recovered",className="text-center"),
                    html.P(
                        "{0:n}".format(daily_data["Daily Recovered"].values[0]),
                        className="card-text text-center",
                    ),
                ],className="w-10",style={"background-color":"#d9f2d9","border-radius": "10px", 
                						 "box-shadow": "2px 2px 2px lightgrey"}
            )
        ]
    card_content_deceased = [
            html.Div(
                [	html.H6("Deceased",className="text-center"),
                    html.P(
                        "{0:n}".format(daily_data["Daily Deceased"].values[0]),
                        className="card-text text-center",
                    ),
                ],className="w-10",style={"background-color":"#d9d9d9", "border-radius": "10px",
                						  "box-shadow": "2px 2px 2px lightgrey"}
            )
        ]
    
    current_status_arrange = [dbc.Row(
        [
            dbc.Col(dbc.Card(card_content_confirmed,)),
            dbc.Col(dbc.Card(card_content_recovered,)),
            dbc.Col(dbc.Card(card_content_deceased,)),
        ],
        className="mb-4"
    ),         
    ]
    card_current_status = [
            dbc.CardBody(
                 current_status_arrange
            ),

            ]
        
    return card_current_status

def get_covid_status_graph():
    case_time_series_data = data_set['case_time_series_data']
    # Create traces
    fig = go.Figure()
    fig.layout.xaxis.zeroline = False
    fig.layout.yaxis.zeroline = False
    #Total Confirmed cases
    fig.add_trace(go.Scatter(x=case_time_series_data.Date, y=case_time_series_data["Total Confirmed"],
                    mode='lines',
                    line_color='#e60000',
                    name='Total Confirmed'))

    #Total Active cases
    fig.add_trace(go.Scatter(x=case_time_series_data.Date, y=case_time_series_data["Total Recovered"] + case_time_series_data["Total Deceased"],
                    mode='lines',
                    fill='tonexty',
                    name='Total Active',
                    showlegend=False,
                    hoverinfo='skip',
                    fillcolor = '#ffeee6',
                    line_color='#993300'))

    #Total Recovered cases
    fig.add_trace(go.Scatter(x=case_time_series_data.Date, y=case_time_series_data["Total Recovered"],
                    mode='lines',
                    name='Total Recovered',
                    line_color='yellowgreen'))

    #Total Deaths
    fig.add_trace(go.Scatter(x=case_time_series_data.Date, y=case_time_series_data["Total Deceased"],
                    mode='lines',
                    fill='tozeroy',
                    name='Total Deceased',
                    fillcolor = 'lightgray',
                    line_color='rosybrown'))

    fig.add_trace(go.Scatter(
    x=["25 March ", "25 March "],
    y=[case_time_series_data["Total Confirmed"].max(),0],
    mode="lines+text",
    name="Lockdown starts",
    text=["Lockdown"],
    textposition="top center",
     hoverinfo='none',
    showlegend=False,
    line_color='#e60000'
    ))

    fig.add_trace(go.Scatter(
    x=["01 June ", "01 June "],
    y=[case_time_series_data["Total Confirmed"].max(),0],
    mode="lines+text",
    name="Unlock 1.0",
    text=["Unlock 1.0"],
    textposition="top center",
     hoverinfo='none',
    showlegend=False,
    line_color='#00b300'
    ))

    fig.add_trace(go.Scatter(
    x=["01 July ", "01 July "],
    y=[case_time_series_data["Total Confirmed"].max(),0],
    mode="lines+text",
    name="Unlock 2.0",
    text=["Unlock 2.0"],
    textposition="top center",
     hoverinfo='none',
    showlegend=False,
    line_color='mediumaquamarine'
    ))
    fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis={"fixedrange": True},
    title={
            'text': "Covid Status in India",
            'y':0.9,
            'x':0.3,
            'xanchor': 'center',
            'yanchor': 'top'},
    autosize=True,
   # width=800,
   # height=500,
    hovermode="x unified",
    margin=dict(
        l=10,
        r=20,
        b=120,
        t=100,
        pad=10),

    )
    
    return fig


def get_overall_status_card(data_set):
    
    cumulative_status_data = covid_curve.get_cumulative_status_data(data_set)

    return html.Div(children=[
    	html.Div([html.H6("Total Confirmed", className="text-danger text-center"),
           		html.P("{0:n}".format(cumulative_status_data['Total Confirmed']),className="text-danger text-center",)],
           		className="mini_container",),

    	html.Div([html.H6("Active Cases", className="text-info text-center"),
           		html.P("{0:n}".format(cumulative_status_data['Active']),className="text-info text-center")],
           		className="mini_container",),

    	html.Div([html.H6("Total Recovered", className="text-success text-center"),
           		html.P("{0:n}".format(cumulative_status_data['Total Recovered']),className="text-success text-center")],
           		className="mini_container",),

    	html.Div([html.H6("Total Deceased",className="text-muted text-center"),
           		html.P("{0:n}".format(cumulative_status_data['Total Deceased']),className="text-muted text-center")],
           		className="mini_container",),
   		],className="two columns")


def get_tests_vs_positive_graph(data_set):
   # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    df = test_positivity.get_tests_vs_positive_data(data_set)
    fig.add_trace(go.Bar(
        x=df["Date"], 
        y=df['Positive'],
        name="Positive Cases",
        marker={'color': '#ff704d'}
    ), secondary_y=False)

    fig.add_trace(go.Bar(
        x=df["Date"], 
        y=df['Number Of Tests'],
        name="Number of tests",
        marker={'color': '#8585ad'}
    ), secondary_y=False)


    # Add traces
    fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Positivity Rate'],
    mode="lines",
    name="Positivity Rate (in %)",
    line_color='#ffbf00'
    ), secondary_y=True)

    # Change the bar mode
    fig.update_layout(barmode='stack',title = "Daily Tests vs Positive Cases",
    	 xaxis={"fixedrange": True},
        autosize=True,
       # width=800,
       # height=500
        margin=dict(
            l=50,
            r=50,
            t=100,
            pad=10),
         hovermode="x unified",
        )
    return fig

def get_tpm_cpm_graph(group_data, population_dict):
    data = []
    for i in group_data.groups.keys():
        data.append(go.Scatter(x=round(group_data.get_group(i)['Positive']/(population_dict[i]/1000000)), 
                           y=round(group_data.get_group(i)['Total Tested']/(population_dict[i]/1000000)), mode="lines",
                           name=i))

    fig = go.Figure(data=data)


    fig.update_layout(
        title= "Test Per Million v/s Case Per Million",
        xaxis={"fixedrange": True},
        # {
        #     'text': "Test Per Million v/s Case Per Million",
        #     'y':0.9,
        #     'x':0.3,
        #     'xanchor': 'center',
        #     'yanchor': 'top'},

        xaxis_title="Case Per Million",
        yaxis_title="Test per million",
        legend_title="States",
        # font=dict(
        #     family="Courier New, monospace",
        #     size=15,
        #     color="RebeccaPurple"
        # )
    )
    
    return fig

def get_tpm_cpm_combined(data_set):

    group_data, population_dict = test_efficiency.get_tpm_cpm_data(data_set)
    
    card = dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs(
                    [
                       dcc.Tab(label='Graph', children=[
                                dcc.Graph(
                                    figure = get_tpm_cpm_graph(group_data, population_dict),
                                  config={'displayModeBar': False})
                            ]),
                        dcc.Tab(label='Table', children=[
                                dbc.Table.from_dataframe(test_efficiency.get_tpm_cpm_table(group_data, population_dict), striped=True, bordered=True, hover=True)
                            ]),
                        #dbc.Tab(label="Tab 2", tab_id="tab-2"),
                    ],
                    id="card-tpm-cpm-tabs",
                    card=True,
                    
                )
            ),
            dbc.CardBody(html.P(id="card-tpm-cpm-content", className="card-text")),
        ]
    )
    
    return card

def get_fatality_state_wise_graph(data_set):
    data_table = fatality.get_fatality_state_wise_data(data_set,state_code_list)
    modeBarButtons = [['toImage']]
    fig = px.bar(data_table, x='State', y='Fatality Rate',width=500,
    	color='Fatality Rate', color_continuous_scale=px.colors.sequential.YlOrRd,
    	)
    fig.update_xaxes(tickangle=45,)
    return fig, data_table

def get_fatality_graph(data_set):
	graph, table = get_fatality_state_wise_graph(data_set)
	card = dbc.Card(
		[
		dbc.CardHeader(
			dbc.Tabs(
				[
				dcc.Tab(label='Graph', children=[
					dcc.Graph(
						figure = graph,config={
					        'modeBarButtons': [['toImage']],
					        'displaylogo': False,
					        'displayModeBar': True
					    })
					]),
				dcc.Tab(label='Table', children=[
					dbc.Table.from_dataframe(table, striped=True, bordered=True, hover=True)
					]),
					#dbc.Tab(label="Tab 2", tab_id="tab-2"),
					],id="card-fatality-tabs",card=True,
					)
			),
		dbc.CardBody(html.P(id="card-fatality-content", className="card-text")),
		])
	return card

def get_total_confirmed_graph(state_wise_data):
    confirmed_data = state_wise_data.sort_values(by=['Confirmed'],ascending=False)
    modeBarButtons = [[ 'toImage']]
    fig = px.bar(confirmed_data, x='State', y='Confirmed',color='Confirmed', color_continuous_scale=px.colors.sequential.Redor,
            title="Total Confirmed Cases")
    fig.update_layout(
    title=dict(x=0.5))
    fig.update_xaxes(tickangle=45,)

    return fig

def get_total_active_graph(state_wise_data):
	active_data = state_wise_data.sort_values(by=['Active'],ascending=False)
	modeBarButtons = [[ 'toImage']]
	fig = px.bar(active_data, x='State', y='Active',color='Active', color_continuous_scale=px.colors.sequential.Bluyl,
            title="Total Active Cases")
	fig.update_layout(
    title=dict(x=0.5))
	fig.update_xaxes(tickangle=45,)
	return fig

def get_total_deaths_graph(state_wise_data):
	death_data = state_wise_data.sort_values(by=['Deaths'],ascending=False)
	modeBarButtons = [[ 'toImage']]
	fig = px.bar(death_data, x='State', y='Deaths',color='Deaths', color_continuous_scale=px.colors.sequential.Burg,
            title="Total Deaths")
	fig.update_layout(
    title=dict(x=0.5))
	fig.update_xaxes(tickangle=45,)
	return fig

radioitems = dbc.FormGroup(
    [
        dbc.RadioItems(
            options=[
                {"label": "Confirmed", "value": 1},
                {"label": "Active", "value": 2},
                {"label": "Deaths", "value": 3},
            ],
            value=1,
            id="radioitems-input",
            inline=True,
        ),
    ]
)

inputs = html.Div(
    [
        dbc.Form(radioitems),
       
    ]
)


@app.callback(
    Output("radio-items", "children"),
    [
        Input("radioitems-input", "value"),
    ],
)
def on_form_change(value):
    state_wise_data = data_set['state_wise_data']
    data = state_wise_data.drop(state_wise_data[state_wise_data['State_code'].isin(['TT','UN'])==True].index)
    if value == 1:
    	return dcc.Graph(figure = get_total_confirmed_graph(data),config={
		        'modeBarButtons': [['toImage']],
		        'displaylogo': False,
		        'displayModeBar': True
		    })
    if value == 2:
    	return dcc.Graph(figure = get_total_active_graph(data),config={
		        'modeBarButtons': [['toImage']],
		        'displaylogo': False,
		        'displayModeBar': True
		    })
    if value == 3:
    	return dcc.Graph(figure = get_total_deaths_graph(data),config={
		        'modeBarButtons': [['toImage']],
		        'displaylogo': False,
		        'displayModeBar': True
		    })

sidebar_header = dbc.Row(
    [
        dbc.Col(html.H2("Explore", className="display-4")),
        dbc.Col(
            [
                
                # html.Button(
                #     # use the Bootstrap navbar-toggler classes to style
                #     html.Span(className="navbar-toggler-icon"),
                    
                #     # the navbar-toggler classes don't set color
                #     style={
                #         "color": "#ffb3b3",
                #         "border-color": "rgba(0,0,0,.1)",
                #         "background-color":"#cccccc",
                #         "width":"30px"
                #     },
                #     id="sidebar-toggle",
                # ),
            ],
            # the column containing the toggle will be only as wide as the
            # toggle, resulting in the toggle being right aligned
            width="auto",
            # vertically align the toggle in the center
            align="center",
        ),
    ]
)

sidebar = html.Div(
    children=[
        sidebar_header,
        html.Hr(),
        # dbc.Collapse(
        dbc.Nav(
            [
                dbc.NavLink("Covid Status", href="#covid-status", id="covid-status-link",external_link=True),
                dbc.NavLink("State Wise Overview", href="#state-overview", id="death-rate-link",external_link=True),
                dbc.NavLink("Test Positivity", href="#test-positivity", id="test-positivity-link",external_link=True),
                dbc.NavLink("Test Efficiency", href="#tpm-cpm", id="tpm-cpm-link",external_link=True),
                dbc.NavLink("Fatality Rate", href="#fatality", id="fatality-link",external_link=True),
            ],
            vertical=True,
            pills=True,
            style={"font-size":"22px"}
        ),
        # )
    ],id="sidebar"
)

content = html.Div([
    	
    	#html.Div(nav),
    	html.Button(
                    # use the Bootstrap navbar-toggler classes to style
                    html.Span(className="navbar-toggler-icon"),
                    
                    # the navbar-toggler classes don't set color
                    style={
                        "color": "#ffb3b3",
                        "border-color": "rgba(0,0,0,.1)",
                        "background-color":"#cccccc",
                        "width":"30px"
                    },
                    id="sidebar-toggle",
                ),
	    dbc.Alert([html.B([
	    	html.P(["Someone is dying in every",
	    		html.Span(alert.get_death_rate(data_set),style={"font-size":"50px","padding-left":"5px","padding-right":"5px"}),"in India!",
	    		]),
	    	],className="text-danger",style={"font-size":"25px"}),], color="danger",
	    className="p-5 text-center",style={"font-size":"large","border-radius": "7px"}),
	    html.Div(get_current_status_card(data_set),id="status",),
	    html.Div([html.P("An outbreak anywhere can go everywhere. We all need to pitch in to try to prevent cases both within ourselves and in our communities."),
        html.P("Flattening the curve is a public health strategy to slow down the spread of the SARS-CoV-2 virus during the COVID-19 pandemic. when virus spread goes up in an exponential way, at one point it exceeds the capacity of total health infrastructure can handle. it leads to failure of health care system of the nation.If individuals and communities take steps to slow the virus’s spread, that means the number of cases of COVID-19 will stretch out across a longer period of time.The number of cases at any given time doesn’t cross the  capacity of the our nation’s health care system to help everyone who’s very sick.Social distancing, wearing maks and washing hands can prevent the failure of health infrastructure")],
        ),
	   	html.Div([
	   		 dbc.Card(
        [
        dbc.CardHeader("Covid Curve In India",style={"font-size":"30px"}),
        dbc.CardBody(
            [
               	dbc.Row([
	   	dbc.Col(html.Div(get_overall_status_card(data_set)),width="60%"),
	   	dbc.Col(html.Div([dcc.Graph(figure = get_covid_status_graph(),
	                   config={'displayModeBar': False,}),
	   	html.Div(html.P("Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.")
	   		,style={"padding":"20px","font-size":"large"})]
	   	))],className="mb-4"),
            ]
        ),
    ],
    )
	   ],id="covid-status"),

	   	# html.Div([
	   	# html.Div([inputs]),
     #    html.Div(id="radio-items"),],className="pretty_container"),

        html.Div([
	   		
	   		 dbc.Card(
        [
        dbc.CardHeader("State-Wise Overview",style={"font-size":"30px"}),
        dbc.CardBody(
            [
               	dbc.Row(
	   			dbc.Col(html.Div([inputs]),className="center-container")
	   			),
	            dbc.Row(
	            dbc.Col(html.Div(id="radio-items"),)
	            )
            ]
        ),
    ],)
	   		],id="state-overview"),

	   	html.Div([
	   		
	   		 dbc.Card(
        [
        dbc.CardHeader("Test Positivity",style={"font-size":"30px"}),
        dbc.CardBody(
            [
               	dbc.Row([
	   			dbc.Col(dcc.Graph(figure = get_tests_vs_positive_graph(data_set),
	                              config={'displayModeBar': False}),
	            ),
	            dbc.Col(html.Div(html.P("Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.")
	   		,className="text_style"),className="center-container")
	            ])
            ]
        ),
    ],)
	   		],id="test-positivity"),

         
	   	html.Div([

	   		dbc.Card(
        [
        dbc.CardHeader("Test Efficiency",style={"font-size":"30px"}),
        dbc.CardBody(
            [
               	dbc.Row(dbc.Col(html.Div(html.P("Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.")
	   		,className="text_style"))),
	   		dbc.Row([
	   		dbc.Col( get_tpm_cpm_combined(data_set),
	           ),
	   		]),
            ]
        ),
    ],)], id="tpm-cpm",),
	        

	   #  html.Div( dbc.Card(
    #     [
    #     dbc.CardHeader("Death Rate",style={"font-size":"30px"}),
    #     dbc.CardBody(
    #         [
    #            	dbc.Row([
	   # 			dbc.Col(dcc.Graph(figure = get_death_rate_graph(data_set),
	   #                            config={'displayModeBar': False}),
	   # 			),
	   #          dbc.Col(html.Div(html.P("Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.")
	   # 		,className="text_style"),className="center-container", width="40%")
	   #          ])
    #         ]
    #     ),
    # ],),id="death-rate",className="pretty_container"),
	    
	    html.Div([
	    	html.H2("Fatality Rate",className="heading_style"),
	    	html.Div(get_fatality_graph(data_set))
	    	],
	    	className="pretty_container",id="fatality"),
	    
	    ],id="content")

@app.callback(
    Output("sidebar", "className"),
    [Input("sidebar-toggle", "n_clicks")],
    [State("sidebar", "className")],
)
def toggle_classname(n, classname):
    if n and classname == "":
        return "collapsed active"
    return ""

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Covid In India",
    brand_href="#",
    color="#8c8c8c",
    fixed="top",
    dark=True,
)

nav_header = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    #dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(dbc.NavbarBrand("Covid In India", className="ml-2",style={"font-size":"30px"})),
                ],
                align="center",
                no_gutters=True,
            ),
            href="/home",
        ),
        #dbc.NavItem(dbc.NavLink("Page 1", href="#fatality")),
        # dbc.NavbarToggler(id="navbar-toggler"),
        # dbc.Collapse(children=[dbc.NavItem(dbc.NavLink("Page 1", href="#fatality")),],id="navbar-collapse", navbar=True),
    ],
    color="#d9d9d9",
    fixed="top",
    #dark=True,
)

nav_footer = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    #dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(dbc.NavbarBrand("Covid In India", className="ml-2",style={"font-size":"30px"})),
                ],
                align="center",
                no_gutters=True,
            ),
            href="/home",
        ),
        #dbc.NavItem(dbc.NavLink("Page 1", href="#fatality")),
        # dbc.NavbarToggler(id="navbar-toggler"),
        # dbc.Collapse(children=[dbc.NavItem(dbc.NavLink("Page 1", href="#fatality")),],id="navbar-collapse", navbar=True),
    ],
    color="#d9d9d9",
    sticky ="bottom",
    #dark=True,
)

footer = html.Footer([
	html.Div([
		html.P("Send your feedback to covidindiadash@gmail.com",),
		html.P("Disclaimer: The information provided by this site is solely based on the data from https://www.covid19india.org/.",
			)
		],className="footer"),
	])

# @app.callback(
#     Output("navbar-collapse", "is_open"),
#     [Input("navbar-toggler", "n_clicks")],
#     [State("navbar-collapse", "is_open")],
# )
# def toggle_navbar_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open

# @app.callback(
#     Output("collapse", "is_open"),
#     [Input("navbar-toggle", "n_clicks")],
#     [State("collapse", "is_open")],
# )
# def toggle_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open

final_body = html.Div([
	    dcc.Location(id='url', refresh=True),
		#html.Div(nav),
		html.Div(nav_header),
		sidebar,
    	content,
],className="wrapper",
)

app.layout = html.Div([

	dbc.Row(
		dbc.Col(final_body)
		),
	dbc.Row(
		dbc.Col(html.Div(footer))
		)
	
	])


if __name__ == '__main__':
    app.run_server(debug=True)
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
import scheduler
import time

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

from apps import utility, alert, covid_curve, test_positivity, death_rate, test_efficiency, fatality, national_overview, state_layout

sched = BackgroundScheduler()

app = dash.Dash(__name__,title="Covid in India",external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.scripts.config.serve_locally = False
app.scripts.append_script({
    'external_url': 'http://www.covidanalyticsindia.org/assets/async_src.js'
})
app.scripts.append_script({
    'external_url': 'http://www.covidanalyticsindia.org/assets/gtag.js'
})

inputs = None
#to get csv data
def get_data():
    global data_set
    print("in get_data")
    data_set = scheduler.get_data()

get_data()

def get_fatality_state_wise_graph(data_set):
    data_table = fatality.get_fatality_state_wise_data(data_set,state_code_list)
    modeBarButtons = [['toImage']]
    fig = px.bar(data_table, x='State', y='Fatality Rate',width=500,
        color='Fatality Rate', color_continuous_scale=px.colors.sequential.YlOrRd,
        )
    fig.update_xaxes(tickangle=45,)
    return fig, data_table

def get_data_dict(data_set):
    data_dict = ""
    data_dict = dict(data_dict)
    data_dict['daily_status'] = alert.get_daily_data(data_set)
    data_dict['cumulative_status'] = covid_curve.get_cumulative_status_data(data_set)
    data_dict['test positivity'] = test_positivity.get_tests_vs_positive_data(data_set)
    data_dict['tpm_cpm_graph_data'] = test_efficiency.get_tpm_cpm_data(data_set)
    data_dict['tpm_cpm_table_data'] = test_efficiency.get_tpm_cpm_table(data_dict['tpm_cpm_graph_data'][0], data_dict['tpm_cpm_graph_data'][1] , data_set)
    data_dict['fatality'] = get_fatality_state_wise_graph(data_set)
    return data_dict

state_code_list = utility.get_state_code_list(data_set)
test_positivity_rate = None
best_states_tpm = None
worst_states_tpm = None
worst_states_death_rate=None
best_states_death_rate=None
data_dict = get_data_dict(data_set)


def get_current_status_card(data_set):
    daily_data = data_dict['daily_status']
    card_content_confirmed = [
            html.Div(
                [	html.H6("Confirmed",className="text-center"),
                    html.Div(
                        html.Strong(f"{int(daily_data['Daily Confirmed'].values[0]):,d}"),
                        className="card-text text-center"
                    ),
                ],style={"background-color":"#ffd6cc",
                						 "box-shadow": "2px 2px 2px lightgrey"}
            )
        ]
    card_content_recovered = [
            html.Div(
                [
                	html.H6("Recovered",className="text-center"),
                    html.P(
                        html.Strong(f"{int(daily_data['Daily Recovered'].values[0]):,d}"),
                        className="card-text text-center",
                    ),
                ],style={"background-color":"#d9f2d9",
                						 "box-shadow": "2px 2px 2px lightgrey"}
            )
        ]
    card_content_deceased = [
            html.Div(
                [	html.H6("Deceased",className="text-center"),
                    html.P(
                        html.Strong(f"{int(daily_data['Daily Deceased'].values[0]):,d}"),
                        className="card-text text-center",
                    ),
                ],style={"background-color":"#d9d9d9",
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
    line_color='#ff751a'
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
    line_color='#ffcc00'
    ))

    fig.add_trace(go.Scatter(
    x=["01 August ", "01 August "],
    y=[case_time_series_data["Total Confirmed"].max(),0],
    mode="lines+text",
    name="Unlock 3.0",
    text=["Unlock 3.0"],
    textposition="top center",
     hoverinfo='none',
    showlegend=False,
    line_color='#99ff33'
    ))

    fig.add_trace(go.Scatter(
    x=["01 September ", "01 September "],
    y=[case_time_series_data["Total Confirmed"].max(),0],
    mode="lines+text",
    name="Unlock 4.0",
    text=["Unlock 4.0"],
    textposition="top center",
     hoverinfo='none',
    showlegend=False,
    line_color='#1f7a1f'
    ))
    fig.update_layout(
    # paper_bgcolor='rgba(0,0,0,0)',
    # plot_bgcolor='rgba(0,0,0,0)',
    xaxis={"fixedrange": True},
    title={
            'text': "Covid Curve in India",
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
    
    cumulative_status_data = data_dict['cumulative_status']

    return html.Div(children=[
    	html.Div([html.H6("Total Confirmed", className="text-danger text-center"),
           		html.P(html.Strong(f"{int(cumulative_status_data['Total Confirmed']):,d}"),className="text-danger text-center",style={"font-size":"15px"})],
           		className="mini_container",),

    	html.Div([html.H6("Active Cases", className="text-info text-center"),
           		html.P(html.Strong(f"{int(cumulative_status_data['Active']):,d}"),className="text-info text-center",style={"font-size":"15px"})],
           		className="mini_container",),

    	html.Div([html.H6("Total Recovered", className="text-success text-center"),
           		html.P(html.Strong(f"{int(cumulative_status_data['Total Recovered']):,d}"),className="text-success text-center",style={"font-size":"15px"})],
           		className="mini_container",),

    	html.Div([html.H6("Total Deceased",className="text-muted text-center"),
           		html.P(html.Strong(f"{int(cumulative_status_data['Total Deceased']):,d}"),className="text-muted text-center",style={"font-size":"15px"})],
           		className="mini_container",),
   		],className="two columns")

def get_tpm_state_comparison(data_table):
     #worst performing states-tpm
    data_table_sorted = data_table.sort_values(by=['Tests Per Million']).dropna(subset=['Tests Per Million'])
    states= []
    for i in data_table_sorted['State'].head(5):
        states.append(i)
    worst_states_tpm = ','.join([str(elem) for elem in states])

    #best performing states-tpm
    states=[]
    for i in data_table_sorted['State'].tail(5):
        states.append(i)
    best_states_tpm = ','.join([str(elem) for elem in states])

    return best_states_tpm, worst_states_tpm

def get_cpm_state_comparison(data_table):
     #best performing states-tpm
    data_table_sorted = data_table.sort_values(by=['Cases Per Million']).dropna(subset=['Cases Per Million'])
    states= []
    for i in data_table_sorted['State'].head(5):
        states.append(i)
    best_states_cpm = ','.join([str(elem) for elem in states])

    #worst performing states-tpm
    states=[]
    for i in data_table_sorted['State'].tail(5):
        states.append(i)
    worst_states_cpm = ','.join([str(elem) for elem in states])

    return best_states_cpm, worst_states_cpm


def get_fatality_rate_state_comparison(table):
    #best performing states - death rate
    states=[]
    for i in table['State'].tail(5):
        states.append(i)
    best_states_death_rate = ','.join([str(elem) for elem in states])

    #worst performing states-death rate
    states=[]
    for i in table['State'].head(5):
        states.append(i)
    worst_states_death_rate = ','.join([str(elem) for elem in states])

    return best_states_death_rate, worst_states_death_rate

def get_test_per_positive_state_comparison(data_table):
    table = data_table.sort_values(by=['Test Per Positive Case']).dropna(subset=['Test Per Positive Case'])
    #best performing states - death rate
    states=[]
    for i in table['State'].tail(5):
        states.append(i)
    best_states = ','.join([str(elem) for elem in states])

    #worst performing states-death rate
    states=[]
    for i in table['State'].head(5):
        states.append(i)
    worst_states = ','.join([str(elem) for elem in states])

    return best_states, worst_states

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

def get_critical_trends_toast(better_states_heading, worst_states_heading,best_states, worst_states):

    content = html.Div([
        html.Div([html.Span(html.B(better_states_heading),style={"font-size":"20px"}),
            html.Br(),
            html.Span(best_states,style={"font-size":"15px","word-wrap": "break-word"})],style={"background-color":"#8dd88d"}),
        html.Div([
            html.Span(html.B(worst_states_heading),style={"font-size":"20px"}),
            html.Br(),
            html.Span(worst_states,style={"font-size":"15px","word-wrap": "break-word"})],style={"background-color":"#ff9980"})
        ],)

    return content

def get_status_toast(today_status, total):

     list_group = dbc.ListGroup(
    [
        dbc.ListGroupItem(
            html.Span([html.Span("In the past 24 hrs: "),
                    html.Strong(f"{int(today_status):,d}")], style={"font-size":"18px","color":"white"}
            ), style={"background-color":"black"}),

        dbc.ListGroupItem(
            html.Span([html.Span("Total: "),
                    html.Strong(f"{int(total):,d}")],style={"font-size":"18px","color":"white"}
            ), style={"background-color":"black"}),
        ])
     return list_group

def get_critical_trends(data_set):

    daily_data = data_dict['daily_status']
    current_date = data_dict['test positivity'][1]
    current_rate  = data_dict['test positivity'][2]
    cumulative_status_data = data_dict['cumulative_status']
    best_states_tpm, worst_states_tpm = get_tpm_state_comparison(data_dict['tpm_cpm_table_data'])
    best_states_cpm, worst_states_cpm = get_cpm_state_comparison(data_dict['tpm_cpm_table_data'])
    best_states_death_rate, worst_states_death_rate = get_fatality_rate_state_comparison(data_dict['fatality'][1])
    best_states_test_positive, worst_states_test_positive = get_test_per_positive_state_comparison(data_dict['fatality'][1])

    confirmed_toast = dbc.Toast(
                [get_status_toast(daily_data['Daily Confirmed'].values[0], cumulative_status_data['Total Confirmed'])],
                header="Confirmed",className="toast_status_style",
                header_style = {
                "padding":"20px",
                "display": "flow-root",
                },
                style={"background-color": "#ff9980"}
            )
    recovered_toast = dbc.Toast(
                [get_status_toast(daily_data['Daily Recovered'].values[0], cumulative_status_data['Total Recovered'])],
                header="Recovered",className="toast_status_style",
                header_style = {
                "padding":"20px",
                "display": "flow-root",
                },
                style={"background-color": "#8dd88d"}
            )
    deceased_toast = dbc.Toast(
                [get_status_toast(daily_data['Daily Deceased'].values[0], cumulative_status_data['Total Deceased'])],
                header="Deceased",className="toast_status_style",
                header_style = {
                "padding":"20px",
                "display": "flow-root",
                },
                style={"background-color": "#999999"}
            )

    test_positivity_toast = dbc.Toast(
                [html.P([html.Span(
                    html.Strong(current_rate), style={"font-size":"20px","padding-top":"15px"}),
                    html.Br(),
                    html.Span(current_date,style={"font-size":"10px","padding-top":"15px"}),
                    ])],
                header="Test Positivity Rate",className="toast_style",
                header_style = {
                "padding":"20px",
                "display": "flow-root",
                }
            )
    
    tpm_toast = dbc.Toast(
                    [get_critical_trends_toast("More Tests","Less Tests",best_states_tpm, worst_states_tpm)],
                    header="Tests Per Million",className="toast_style",
                    header_style = {
                    "padding":"20px",
                    "display": "flow-root",
                    }
                )

    cpm_toast = dbc.Toast(
                    [get_critical_trends_toast("Less Cases","More Cases",best_states_cpm, worst_states_cpm)],
                    header="Cases Per Million",className="toast_style",
                    header_style = {
                    "padding":"20px",
                    "display": "flow-root",
                    }
                )

    fatality_toast = dbc.Toast(
                    [get_critical_trends_toast("Low Fatality Rate","High Fatality Rate",best_states_death_rate, worst_states_death_rate)],
                    header="Fatality Rate",className="toast_style",
                    header_style = {
                    "padding":"20px",
                    "display": "flow-root",
                    }
                )
    test_positive_toast = dbc.Toast(
                    [get_critical_trends_toast("More Efficient Testing","Less Efficient Testing",best_states_test_positive, worst_states_test_positive)],
                    header="Test Per Positive Case",className="toast_style",
                    header_style = {
                    "padding":"20px",
                    "display": "flow-root",
                    }
                )

    table = html.Div([
        html.Div([
        dbc.Row([
        dbc.Col(confirmed_toast),
        dbc.Col(recovered_toast),
        dbc.Col(deceased_toast)]),],style={"padding-left":"10px"}),

        html.Div([
        dbc.Row([
        dbc.Col(cpm_toast, className="col-6 d-flex justify-content-center"),
        dbc.Col(tpm_toast, className="col-6 d-flex justify-content-center"),
        ])],style={"padding":"20px","align":"center"}),

        html.Div([
        dbc.Row([
        dbc.Col(fatality_toast, className="col-6 d-flex justify-content-center"),
        dbc.Col(test_positive_toast, className="col-6 d-flex justify-content-center")
        ])],style={"padding":"20px","align":"center"}),

        ])

    return table

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
            labelClassName="date-group-labels",
            labelCheckedClassName="date-group-labels-checked",
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

navbar = html.Div([
        dbc.Nav(
            [   dbc.NavLink("Critical Trends", href="#critical_trends", id="critical-trends-link",external_link=True),
                dbc.NavLink("Covid Status", href="#covid-status", id="covid-status-link",external_link=True),
                dbc.NavLink("National Overview", href="/national_view", id="death-rate-link",external_link=True),
                dbc.NavLink("About",href="/about", id="about-link",external_link=True)
            ],
            horizontal=False,
            fill = True,
            className = "link-style"
            
        ),
        ]
        )

about = html.Div([
    html.H1('About'),
    html.Div(id='page-2-content'),
    html.Br(),
    html.Div([
        html.P("The main objective of this site is to provide analytical picture of India's battle against Covid in a very simple manner. Various parameters chosen here is to measure the impact of the pandemic in the best possible way.")]),
        html.P("The raw data is obtained from https://www.covid19india.org/."),
        html.P("References: https://ourworldindata.org/, https://www.thehindu.com/"),
        html.P("Send your feedback to covid19analyticsindia@gmail.com"),
        dcc.Link('Go to dashboard', href = "/")
],style={"text-align": "center","justify-content":"center"},id="about")

# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/about':
        return about
    elif pathname == '/national_view':
        return national_overview.get_national_overview(data_dict, data_set)
    else:
        return index_page

nav_header = dbc.Navbar(
    [
        dbc.Row([
            dbc.Col(html.Strong("COVID IN INDIA",),className="nav_header", width=12),
            dbc.Col(navbar)
            ], className = "nav_row_style")
    ],
    color="#6c757d",
    fixed="top",
)


#################################################################################################

#State Page

def get_state_list():
    state_code_list = utility.get_state_code_list(data_set)
    state_list = state_code_list.drop(state_code_list[state_code_list['State'].isin(['State Unassigned'])==True].index)
    state_list.sort_values(by=['State'],inplace=True)
    return state_list

def get_tpm_cpm_values(state):
    tpm_cpm_data = data_dict['tpm_cpm_table_data']
    tpm_state = tpm_cpm_data[tpm_cpm_data['State']== state]['Tests Per Million'].values[0]
    cpm_state = tpm_cpm_data[tpm_cpm_data['State']== state]['Cases Per Million'].values[0]
    return tpm_state, cpm_state

def get_fatality_test_positivity_data(state):
    data = data_dict['fatality'][1]
    fatality_state = data[data['State']== state]['Fatality Rate'].values[0]
    test_per_positive = data[data['State']== state]['Test Per Positive Case'].values[0]
    return fatality_state, test_per_positive


@app.callback(
    dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_output(state):
    data_dict['tpm_cpm_values'] = get_tpm_cpm_values(state)
    data_dict['fatality_test_positivity_values'] = get_fatality_test_positivity_data(state)
    return state_layout.get_state_layout(data_set, state, data_dict)

#################################################################################################

def get_home_content(data_set, data_dict):
    print("in home content")
    global inputs

    content = html.Div([
        	html.Div([
    	    dbc.Alert([html.B([
    	    	html.P([html.Span("Someone is dying in every",),
    	    		html.Span([html.Span(alert.get_death_rate(data_set),style={"font-size":"30px","font-family": "Catamaran","padding-left":"5px","padding-right":"5px"}),]),
    	    		html.Span(["in ", html.Span("India!",style={"font-size":"25px","font-family": "Catamaran","padding-left":"5px",}),]),
    	    		]),
    	    	],className="text-danger",style={"font-size":"25px","font-family": "Catamaran"}),], color="danger",
    	    className="p-5 text-center",style={"font-size":"large","border-radius": "7px"}),
    	    html.Div(get_current_status_card(data_set),id="status",),
    	    html.Div([html.P(html.Strong("An outbreak anywhere can go everywhere. We all need to pitch in to try to prevent cases both within ourselves and in our communities.",className="text_style",style={"padding-bottom":"5px","padding-top":"10px"}),style={"text-align": "center","padding-top":"10px"}),
            html.P("Flattening the curve is a public health strategy to slow down the spread of the SARS-CoV-2 virus during the COVID-19 pandemic. When virus spread goes up in an exponential way, at one point it exceeds the capacity which total health infrastructure can handle. It leads to failure of health care system of the nation. If individuals and communities take steps to slow the virus’s spread, that means the number of cases of COVID-19 will stretch out across a longer period of time. So that we can keep the number of cases at any given time doesn’t cross the  capacity of the our nation’s health care system to help everyone who’s very sick. Social distancing, wearing masks and washing hands are some effective ways to prevent the spred of the pandemic.",className="text_style")],
            className="pretty_container"),

            html.Div([
                html.H2("Critical Trends", className="heading_style"),
                html.Div([get_critical_trends(data_set)]),
                html.Div("Scroll on to know each factor in detail!!!",
                    style={"font-size":"20px","padding":"20px","font-weight": "bold","font-style": "italic"})
                ],className="pretty_container",id="critical_trends"),

    	   	html.Div([
    	   		 dbc.Card(
            [
            dbc.CardHeader("Covid Curve In India",style={"font-size":"30px"}),
            dbc.CardBody(
                [
                   	dbc.Row([
    	   	dbc.Col(html.Div(get_overall_status_card(data_set)),width="60%"),
    	   	dbc.Col(html.Div([dcc.Graph(figure = get_covid_status_graph(),
    	                   config={
    					        'modeBarButtons': [['toImage']],
    					        'displaylogo': False,
    					        'displayModeBar': True
    					    }),
    	   	html.Div([html.P([
                html.Span("The goal of every nation is to "),
                html.Span(html.B("flatten the covid curve ")),
                html.Span("by reducing the number of active cases and finally reaching to zero. This plot depicts how India responds to covid day by day. The cumulative number of covid cases is plotted against the day since the first covid case reported on January 30, 2020. It also shows the total number of recovered and deceased till today.")]),
    	   	 html.P("This also indicates how the covid cases are rapidly increasing after each unlock phase. Here comes the question, whether the lockdown was really efficient in containing the pandemic?"),
    	   	 html.P("One thing to be noted is the number of confirmed cases is lower than the actual cases due to limited testing. Also, the reported cases on a date may not necessarily be the actual number of cases on that day due to delayed reporting.")]
    	   		,className="text_style")]
    	   	))],className="mb-4"),
                ]
            ),
        ],
        )
    	   ],id="covid-status"),

            html.Div([
    	   		
    	   		 dbc.Card(
            [
            dbc.CardHeader("State-Wise Overview",style={"font-size":"30px"}),
            dbc.CardBody(
                [
                   	dbc.Row(
    	            dbc.Col(html.Div(html.P("The purpose of this graph is to give a picture of the states affected by covid. This helps to gauge each state in terms of confirmed cases, active cases, and deaths. ")
            		,className="text_style"),)
    	            ),
                   	dbc.Row([
    	   			dbc.Col(html.Div([inputs]),className="center-container",width=10),
                    # dbc.Col(html.Div(dbc.NavLink("Click Here to Know More on States",href="/state_view", id="state_link",external_link=True,className="link_style"),
                    #         style={"background-color": "#d62d3d"},className="nav_button ml-auto flex-nowrap mt-3 mt-md-0"))
                    ]
    	   			),
    	            dbc.Row(
    	            dbc.Col(html.Div(id="radio-items"),),
                    ),
                    dbc.Row(
                        dbc.Col(html.Div("Choose a state to know more!"))),
                    dbc.Row([
                        dbc.Col(html.Div([
                            dcc.Dropdown(
                                id='dropdown',
                                options=[{"label": state, "value": state} for state in get_state_list()['State']],
                                value='Delhi'
                            ),
                            html.Div(id='dd-output-container')
                        ]))
                        ], style={"margin-top":"20px"})
            ]),
        ],)
    	   		],id="state-overview"),
    	    
    	    ],id="content")])

    return content

footer = html.Footer([
	html.Div([
		html.P([html.Span("Send your feedback to "),
            html.Strong("covid19analyticsindia@gmail.com")]),
		html.P("Disclaimer: The information provided by this site is solely based on the data from https://www.covid19india.org/.",
			),
        html.P(html.P(dbc.NavLink("About",href="/about", id="about_link",external_link=True,className="link_style"),className="nav_button",style={"display": "inline-block"}),
            style={"background-color": "#404040", "padding": "10px"})
		],className="footer"),
	])

home_page_content = get_home_content(data_set, data_dict)

index_page = html.Div([
    nav_header,
    html.Div(home_page_content,style={"padding-top": "100px"}),
    footer])

app.layout = html.Div([
	    dcc.Location(id='url', refresh=True),
        html.Div(id='page-content')
],
)


@sched.scheduled_job('cron', day_of_week='mon-sun', hour=1)
def scheduled_job():
    global index_page,data_set,data_dict
    print('This job runs every day at 2 am.')
    get_data()

    index_page = html.Div([
    nav_header,
    html.Div(get_home_content(data_set,data_dict),style={"padding-top": "100px"}),
    footer])

sched.start()

if __name__ == '__main__':
    app.run_server(debug=True)
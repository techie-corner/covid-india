#State Page
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
import time

from apps import utility, covid_curve, test_positivity

data_set = None

def get_total_confirmed(state):
    data =  data_set['state_wise_data']
    return data[data['State']==state]['Confirmed'].values[0]

def get_total_recovered(state):
    data =  data_set['state_wise_data']
    return data[data['State']==state]['Recovered'].values[0]

def get_total_deceased(state):
    data =  data_set['state_wise_data']
    return data[data['State']==state]['Deaths'].values[0]

def get_today_status(data_set, state):
    state_wise_daily_data = data_set['state_wise_daily_data']
    state_code = utility.get_state_code(data_set, state)
    confirmed = state_wise_daily_data.tail(3)[state_code].values[0]
    recovered = state_wise_daily_data.tail(3)[state_code].values[1]
    deaths = state_wise_daily_data.tail(3)[state_code].values[2]

    return confirmed,recovered,deaths

def get_covid_status_state_graph(state):

    data = covid_curve.get_state_wise_data(data_set, state)
    # Create traces
    fig = go.Figure()
    fig.layout.xaxis.zeroline = False
    fig.layout.yaxis.zeroline = False
    #Total Confirmed cases
    fig.add_trace(go.Scatter(x=data.Date, y=data["Confirmed"],
                    mode='lines',
                    line_color='#e60000',
                    name='Total Confirmed'))

    #Total Recovered cases
    fig.add_trace(go.Scatter(x=data.Date, y=data["Recovered"],
                    mode='lines',
                    name='Total Recovered',
                    line_color='yellowgreen'))

    #Total Deaths
    fig.add_trace(go.Scatter(x=data.Date, y=data["Deceased"],
                    mode='lines',
                    fill='tozeroy',
                    name='Total Deceased',
                    fillcolor = 'lightgray',
                    line_color='rosybrown'))

    fig.add_trace(go.Scatter(
    x=["Mar 25,2020 ", "Mar 25,2020 "],
    y=[data["Confirmed"].max(),0],
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
    y=[data["Confirmed"].max(),0],
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
    y=[data["Confirmed"].max(),0],
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
    y=[data["Confirmed"].max(),0],
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
    y=[data["Confirmed"].max(),0],
    mode="lines+text",
    name="Unlock 4.0",
    text=["Unlock 4.0"],
    textposition="top center",
     hoverinfo='none',
    showlegend=False,
    line_color='#1f7a1f'
    ))

    graph_title = 'Covid Curve in {}'.format(state)
    fig.update_layout(
    # paper_bgcolor='rgba(0,0,0,0)',
    # plot_bgcolor='rgba(0,0,0,0)',
    xaxis={"fixedrange": True},
    title={
            'text': graph_title,
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

def get_state_test_positivity(state):
    df = data_set['state_test_positivity'][0]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=df["Date"], 
        y=df['Positive'],
        name="Positive Cases",
        text=['Positive Cases'],
        marker={'color': '#ff704d'},
        width=0.8
    ), secondary_y=False)

    fig.add_trace(go.Bar(
        x=df["Date"], 
        y=df['Number Of Tests'],
        name="Number of tests",
        marker={'color': '#8585ad'},
        width=0.8
    ), secondary_y=False)


    # Add traces
    fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Positivity Rate'],
    mode="lines",
    name="Positivity Rate",
    line_color='#ffbf00'
    ), secondary_y=True)

    # Change the bar mode
    fig.update_layout(barmode='stack',title = "Daily Tests vs Positive Cases",
         xaxis={"fixedrange": True},
        autosize=True,
        # width=800,
        # height=600,
        legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-1,
        xanchor="right",
        x=1
        ),
        margin=dict(
            l=50,
            r=50,
            t=100,
            pad=10),
         hovermode="x unified",
        yaxis2 = dict(
            titlefont=dict(
                color="#ffbf00"
            ),
            tickfont=dict(
                color="#ffbf00"
            ),
            #tickformat = '%',
            anchor="x",
            overlaying="y",
            side="right"
        ),
        )
    fig.update_yaxes(title_text="Number of tests", secondary_y=False)
    fig.update_yaxes(title_text="Positivity Rate", secondary_y=True)

    return fig

def get_state_tpm_cpm_graph(data_set, state, data_dict):
    data1= []
    group_data, population_dict = data_dict['tpm_cpm_graph_data']
    data = group_data.get_group(state)
    data1.append(go.Scatter(x=round(data['Positive']/(population_dict[state]/1000000)), 
                           y=round(data['Total Tested']/(population_dict[state]/1000000)), mode="lines",
                           name=state))

    fig = go.Figure(data=data1)

    fig.update_layout(
        title={
        'text': "Tests Per Million v/s Cases Per Million",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        # width=800,
        # height=600,
        xaxis={"fixedrange": True},
        xaxis_title="Cases Per Million",
        yaxis_title="Tests per million",
        # legend_title=value,
    )
    graph = dcc.Graph(
        figure = fig,
        config={
    'modeBarButtons': [['toImage']],
    'displaylogo': False,
    'displayModeBar': True
    })

    return graph

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

def get_critical_trends(state):

    confirmed, recovered, deceased = get_today_status(data_set, state)
    confirmed_toast = dbc.Toast(
                [get_status_toast(confirmed, get_total_confirmed(state))],
                header="Confirmed",className="toast_status_style",
                header_style = {
                "padding":"20px",
                "display": "flow-root",
                },
                style={"background-color": "#ff9980"}
            )
    recovered_toast = dbc.Toast(
                [get_status_toast(recovered, get_total_recovered(state))],
                header="Recovered",className="toast_status_style",
                header_style = {
                "padding":"20px",
                "display": "flow-root",
                },
                style={"background-color": "#8dd88d"}
            )
    deceased_toast = dbc.Toast(
                [get_status_toast(deceased, get_total_deceased(state))],
                header="Deceased",className="toast_status_style",
                header_style = {
                "padding":"20px",
                "display": "flow-root",
                },
                style={"background-color": "#999999"}
            )

    table = html.Div([
        html.Div([
        dbc.Row([
        dbc.Col(confirmed_toast),
        dbc.Col(recovered_toast),
        dbc.Col(deceased_toast)]),],style={"padding-left":"10px"}),
        ])

    return table

nav_header = dbc.Navbar(
    [
            dbc.Row(
                [
                    dbc.Row(
                    dbc.Col("",width=6),
                    ),
                    ],style={"padding-left":"15px"}),
                    dbc.Row(
                    dbc.Col(dbc.NavLink("Go to Dashboard",href="/",external_link=True,className="link_style nav_button"))
                    ,className="ml-auto flex-nowrap mt-3 mt-md-0",style={"padding-right":"15px"}),
    ],
    color="#6c757d",
    fixed="top",
)

def get_state_layout(data, state, data_dict):
    global data_set
    data_set = data
    data_set['state_test_positivity'] = test_positivity.get_state_positivity_data(data_set, state)
    content = html.Div([
            html.Div([
            # dbc.Alert([html.B([
            #     html.P([html.Span("Someone is dying in every",),
            #         html.Span([html.Span(alert.get_death_rate(data_set),style={"font-size":"30px","font-family": "Catamaran","padding-left":"5px","padding-right":"5px"}),]),
            #         html.Span(["in ", html.Span("India!",style={"font-size":"25px","font-family": "Catamaran","padding-left":"5px",}),]),
            #         ]),
            #     ],className="text-danger",style={"font-size":"25px","font-family": "Catamaran"}),], color="danger",
            # className="p-5 text-center",style={"font-size":"large","border-radius": "7px"}),
            html.Div(html.Strong(state),style={"display": "flex","justify-content": "center","font-size": "50px"}),
            html.Div([
                html.Div([
                html.Div([get_critical_trends(state)]),
                ],id="critical_trends"),
                    ], style={"padding":"15px"}),

            html.Div(
                 dbc.Card([
            dbc.CardHeader("Covid Curve",style={"font-size":"30px"}),
            dbc.CardBody(
                
                    html.Div(dcc.Graph(figure = get_covid_status_state_graph(state),
                           config={
                                'modeBarButtons': [['toImage']],
                                'displaylogo': False,
                                'displayModeBar': True
                            }),
            ))]),style={"padding":"15px"}),

            html.Div([
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
                [
                dbc.CardHeader("Test Positivity Rate",className="text-center",style={"background-color":"#ffb3b3","font-weight":"bold"}),
                dbc.CardBody(data_set['state_test_positivity'][2].values[0]
                    , className="card-text text-center",style={"display": "flex","align-items": "center",
    "justify-content": "center","background-color":"black","color":"white","border-radius": "0px 0px 20px 20px","font-weight":"bold"} 
                ),
            ],className="card_style")
                        ),
                    dbc.Col(
                        dbc.Card(
                [
                dbc.CardHeader("Tests Per Million",className="text-center",style={"background-color":"#99ffeb","font-weight":"bold"}),
                dbc.CardBody(f"{int(data_dict['tpm_cpm_values'][0]):,d}"
                    ,className="card-text text-center",style={"display": "flex","align-items": "center",
    "justify-content": "center","background-color":"black","color":"white","border-radius": "0px 0px 20px 20px","font-weight":"bold"} 
                ),
            ],className="card_style")
                        ),
                    dbc.Col(
                        dbc.Card(
                [
                dbc.CardHeader("Cases Per Million",className="text-center",style={"background-color":"#ccffb3","font-weight":"bold"}),
                dbc.CardBody(f"{int(data_dict['tpm_cpm_values'][1]):,d}"
                    ,className="card-text text-center",style={"display": "flex","align-items": "center",
    "justify-content": "center","background-color":"black","color":"white","border-radius": "0px 0px 20px 20px","font-weight":"bold"} 
                ),
            ],className="card_style"),
                        ),
                    dbc.Col(
                        dbc.Card(
                [
                dbc.CardHeader("Fatality Rate",className="text-center",style={"background-color":"#ffffb3","font-weight":"bold"}),
                dbc.CardBody("{}%".format(data_dict['fatality_test_positivity_values'][0])
                    ,className="card-text text-center",style={"display": "flex","align-items": "center",
    "justify-content": "center","background-color":"black","color":"white","border-radius": "0px 0px 20px 20px","font-weight":"bold"} 
                ),
            ],className="card_style"),
                        ),
                    dbc.Col(
                        dbc.Card(
                [
                dbc.CardHeader("Tests Per Positive Case",className="text-center",style={"background-color":"#ffb3ff","font-weight":"bold"}),
                dbc.CardBody(f"{int(data_dict['fatality_test_positivity_values'][1]):,d}"
                    ,className="card-text text-center",style={"display": "flex","align-items": "center",
    "justify-content": "center","background-color":"black","color":"white","border-radius": "0px 0px 20px 20px","font-weight":"bold"} 
                ),
            ],className="card_style"),
                        )
                    ])
                
                
                
                ], id="tpm-cpm",style={"padding":"15px"}),


            html.Div([
                dbc.Row([
                    dbc.Col(
                        dbc.Card(
            [
            dbc.CardHeader("Test Positivity",style={"font-size":"30px"}),
            dbc.CardBody(
                [

                html.Div(
                            dcc.Graph(figure = get_state_test_positivity(state),
                                              config={
                                        'modeBarButtons': [['toImage']],
                                        'displaylogo': False,
                                        'displayModeBar': True
                                    }),style={"justify-content":"center"}),

                ]
            ),
        ],)
                        ),
                    dbc.Col(
                        dbc.Card(
            [
            dbc.CardHeader("Test Efficiency",style={"font-size":"30px"}),
            dbc.CardBody(
                [
                 html.Div(get_state_tpm_cpm_graph(data_set, state, data_dict),
                    style={"justify-content":"center"})
                
                ]
            ),
        ],)
                        )
                    ])
                 
                ],id="test-positivity",style={"padding":"15px"}),

            html.Div([
                dbc.Card([
                    dbc.CardHeader("Terms And Definitions",style={"font-size":"30px"}),
                    dbc.CardBody(
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                html.P([
                                    html.Strong("Test Positivity"),
                                    html.Span(": is the rate of the spread of the infectious virus in an area.")
                                    ])
                                ]),
                            dbc.ListGroupItem([
                                html.P([
                                    html.Strong("Tests Per Million"),
                                    html.Span(": is a measure of how effective the tests are done in the state.")
                                    ])
                                ]),
                            dbc.ListGroupItem([
                                html.P([
                                    html.Strong("Cases Per Million"),
                                    html.Span(": is a measure of how many people are tested positive in a million of state's population.")
                                    ])
                                ]),
                            dbc.ListGroupItem([
                                html.P([
                                    html.Strong("Fatality Rate"),
                                    html.Span(": depicts the fact that how likely someone who catches the disease would die. ")
                                    ])
                                ]),
                            dbc.ListGroupItem([
                                html.P([
                                    html.Strong("Tests Per Positive Case"),
                                    html.Span(": a measure of how effectively testing is done in a state. The higher the number, testing is more efficient and extensive in those states.")
                                    ])
                                ]),
                            ])
                        )
                    ])
                ])
            
        ],id="content")])

    return content


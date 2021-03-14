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


nav_header = html.Div(
	dbc.Navbar(
        dbc.Nav(
            [   dbc.NavLink("Test Positivity", href="#test-positivity", id="test-positivity-link",external_link=True,className="link_style"),
                dbc.NavLink("Test Efficiency", href="#tpm-cpm", id="tpm-cpm-link",external_link=True,className="link_style"),
                dbc.NavLink("Fatality Rate", href="#fatality", id="fatality-link",external_link=True,className="link_style"),
                dbc.NavLink("Go to Dashboard",href="/",external_link=True,className="link_style")
            ],
            horizontal=False,
            fill = True,
            className = "link-style"
            
        ),
        color="#6c757d",
		fixed="top")
        )

def get_tests_vs_positive_graph(data_set, data_dict):
   
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    df,current_date,current_rate = data_dict['test positivity']
    fig.add_trace(go.Bar(
        x=df["Date"], 
        y=df['Positive'],
        name="Positive Cases",
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
        width=800,
        height=600,
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
            dtick = 0.5,
            #tickformat = '%',
            anchor="x",
            overlaying="y",
            side="right"
        ),
        )
    fig.update_yaxes(title_text="Number of tests", secondary_y=False)
    fig.update_yaxes(title_text="Positivity Rate", secondary_y=True)
    return fig


def get_tpm_cpm_graph(group_data, population_dict):
    data = []
    for i in group_data.groups.keys():
        data.append(go.Scatter(x=round(group_data.get_group(i)['Positive']/(population_dict[i]/1000000)), 
                           y=round(group_data.get_group(i)['Total Tested']/(population_dict[i]/1000000)), mode="lines",
                           name=i))

    fig = go.Figure(data=data)


    fig.update_layout(
        title= "Tests Per Million v/s Cases Per Million",
        xaxis={"fixedrange": True},
        xaxis_title="Cases Per Million",
        yaxis_title="Tests per million",
        legend_title="States",
    )
    
    return fig

def get_tpm_cpm_combined(data_set, data_dict):

    group_data, population_dict = data_dict['tpm_cpm_graph_data']
    data_table = data_dict['tpm_cpm_table_data']

    card = dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs(
                    [
                       dcc.Tab(label='Graph', children=[
                                dcc.Graph(
                                    figure = get_tpm_cpm_graph(group_data, population_dict),
                                  config={
					        'modeBarButtons': [['toImage']],
					        'displaylogo': False,
					        'displayModeBar': True
					    })
                            ]),
                        dcc.Tab(label='Table', children=[
                                dbc.Table.from_dataframe(data_table, striped=True, bordered=True, hover=True)
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

def get_fatality_graph(data_set, data_dict):
	graph, table = data_dict['fatality']
	states= []
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

def get_national_overview(data_dict, data_set):

    content = html.Div([
		nav_header,
		html.Div([
    	   		html.H2("National Overview", style={"display":"flex", "justify-content":"center","margin-top":"100px"}),
    	   		 dbc.Card(
            [
            dbc.CardHeader("Test Positivity",style={"font-size":"30px"}),
            dbc.CardBody(
                [
                html.Div([html.P("Is India performing adequate tests?",style={"font-size":"25px"}),
                        html.P("Since tests are the only means to identify covid cases, a country needs to perform tests on a maximum number of people, which would help to know the degree of spread in an area. In an ideal case, it should test all the people in the country. But this is not practical due to the limited testing facilities."),
                        html.P([
                            html.Span("The "),
                            html.Span(html.B("test positivity rate")),
                            html.Span(" is a measure of the spread of the infectious virus in an area. It throws light on the size of the outbreak and the requirement to increase the tests. "),
                            html.Span(html.B("According to WHO, the test positivity rate should be lower than 10%, but better less than 3% as a benchmark for adequate testing")),
                            html.Span(". In other words, 10 - 30 tests per confirmed case indicates a fair level of testing."),]),
                        html.P("If the positivity rate does not fall within this benchmark, it indicates that the country is not performing adequate tests. And the reported positive cases are only a fraction of the actual cases."),
                        html.P([html.Span("This graph shows the total number of cases, confirmed cases, and test positivity rate each day, for the past two weeks. India has a test positivity rate of "),
                            html.Span(html.B(data_dict['test positivity'][2])),
                            html.Span(html.B("% ")),
                            html.Span("on "),
                            html.Span(html.B(data_dict['test positivity'][1])),
                            html.Span(".")])]
                ,className="text_style"),

                html.Div(
                    dcc.Graph(figure = get_tests_vs_positive_graph(data_set, data_dict),
                                      config={
                                'modeBarButtons': [['toImage']],
                                'displaylogo': False,
                                'displayModeBar': True
                            }),style={"display": "flex","align-items": "center","justify-content": "center"}),
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
                   	dbc.Row(dbc.Col(html.Div([html.P("Why testing is very much essential?",style={"font-size":"25px"}),
                        html.P([
                            html.Span("As we all know, in the current scenario where exact methods to tackle the pandemic are still uncertain and the whole world is trying hard to get a medicine for the same, the only way to contain the virus is by testing extensively to track the infectious people and trace their contacts. In that light, Tests per million and Cases per million would give us an idea about the spread of the virus. "),
                            html.Span(html.B("Measuring a region’s testing rate in comparison to its outbreak size will help identify those which are not testing enough. "))]),
                   		html.P([
                            html.Span("The graph shows the tests per million(vertical axis) v/s cases per million(horizontal axis) for different states daily from April 17, 2020. "),
                            html.Span(html.B("Steeper the line in the upward direction, testing in those states is relatively higher than the confirmed cases, which is the desirable condition. ")),
                            html.Span("Otherwise, it shows that the testing is insufficient in those states, and the number of actual cases in those states might be far higher than reported.")]),
                   		html.P("The table gives the present tests per million and cases per million of each state."),
                        html.P("Double-click on the state name to view individual trend!",style={"font-size":"20px","padding":"20px","font-weight": "bold","font-style": "italic"})]
    	   		,className="text_style"))),
    	   		dbc.Row([
    	   		dbc.Col( get_tpm_cpm_combined(data_set, data_dict),
    	           ),
    	   		]),
                ]
            ),
        ],)], id="tpm-cpm",),


    	   	html.Div([

                dbc.Card(
            [
            dbc.CardHeader("Fatality Rate",style={"font-size":"30px"}),
            dbc.CardBody(
                [
                    dbc.Row([
                dbc.Col(html.Div(
                    [html.P("How crucial is the pandemic?",style={"font-size":"25px"}),
                    html.P([
                        html.Span("To understand the risk and to timely respond, we would also need to get the fatality rate. "),
                        html.Span(html.B("Fatality Rate depicts the fact that how likely someone who catches the disease would die. ")),
                        html.Span("Comparing the COVID-19 case curves of different states is the most widely used tool to measure the effectiveness of a particular state’s response to the pandemic. However, as the rate of testing differs widely across states, case curves may not be a sufficient tool. The fatality rate may present a better picture. This is measured by taking the ratio of total confirmed deaths by the total confirmed cases. But during the pandemic, it would be really difficult to analyze the risk of the pandemic by looking at the fatality rate, since the data might be incomplete. Here, the plot compares various states on the fatality rate.")]),
                    html.P(html.B("Test per positive case is a measure of how effectively testing is done in a state. The higher the number, testing is more efficient and extensive in those states."))]
                    ,className="text_style")
                   ),
                ]),
                    dbc.Row(dbc.Col(get_fatality_graph(data_set, data_dict))),
                
                ]
            ),
        ],)], id="fatality",),

		])
    return content



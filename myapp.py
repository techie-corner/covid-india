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

app = dash.Dash(__name__,title="Covid in India",external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

mini_container = {
    "border-radius": "5px",
    "background-color": "#f9f9f9",
    "margin": "10px",
    "padding": "15px",
    "position": "relative",
    "box-shadow": "2px 2px 2px lightgrey",
    }

target_url = 'https://api.covid19india.org/csv/latest/case_time_series.csv'
case_file = pd.read_csv (target_url)
test_file_location = "https://api.covid19india.org/csv/latest/statewise_tested_numbers_data.csv"
test_data = pd.read_csv(test_file_location)
state_wise_daily_url = 'https://api.covid19india.org/csv/latest/state_wise_daily.csv'
state_wise_daily_data = pd.read_csv (state_wise_daily_url)

def get_death_rate():
    total_days = (len(case_file)*24*60*60)
    total_deaths = case_file['Daily Deceased'].sum()
    death_rate = total_days/total_deaths
    minutes, sec = divmod(death_rate, 60) 
    hour, minutes = divmod(minutes, 60)
    alert_string = ''
    if hour > 0:
       alert_string += '{} hours '.format(int(hour))
    if minutes > 0:
    	alert_string += '{} minutes '.format(int(minutes))
    if sec > 0:
    	alert_string += '{} seconds'.format(int(sec))
    return alert_string
    
def get_covid_status_graph():
    # Create traces
    fig = go.Figure()
    fig.layout.xaxis.zeroline = False
    fig.layout.yaxis.zeroline = False
    #Total Confirmed cases
    fig.add_trace(go.Scatter(x=case_file.Date, y=case_file["Total Confirmed"],
                    mode='lines',
                    line_color='#e60000',
                    name='Total Confirmed'))

    #Total Active cases
    fig.add_trace(go.Scatter(x=case_file.Date, y=case_file["Total Recovered"] + case_file["Total Deceased"],
                    mode='lines',
                    fill='tonexty',
                    name='Total Active',
                    showlegend=False,
                    hoverinfo='skip',
                    fillcolor = '#ffeee6',
                    line_color='#993300'))

    #Total Recovered cases
    fig.add_trace(go.Scatter(x=case_file.Date, y=case_file["Total Recovered"],
                    mode='lines',
                    name='Total Recovered',
                    line_color='yellowgreen'))


    fig.add_trace(go.Scatter(x=case_file.Date, y=case_file["Total Deceased"],
                    mode='lines',
                    fill='tozeroy',
                    name='Total Deceased',
                    fillcolor = 'lightgray',
                    line_color='rosybrown'))

    fig.add_trace(go.Scatter(
    x=["25 March ", "25 March "],
    y=[case_file["Total Confirmed"].max(),0],
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
    y=[case_file["Total Confirmed"].max(),0],
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
    y=[case_file["Total Confirmed"].max(),0],
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


def get_daily_data():
    daily_data = case_file.tail(1)
    return daily_data[["Daily Confirmed","Daily Recovered","Daily Deceased"]]

def get_cumulative_status_data():
    cumulative_data = case_file.tail(1)
    return cumulative_data[["Total Confirmed","Total Recovered","Total Deceased"]]

def get_total_death_data():
    return get_cumulative_status_data()["Total Deceased"].values[0]

def get_total_recovered_data():
    return get_cumulative_status_data()["Total Recovered"].values[0]

def get_total_confirmed_data():
    return get_cumulative_status_data()["Total Confirmed"].values[0]

def get_total_active_data():
    return (get_total_confirmed_data() - (get_total_recovered_data() + get_total_death_data()))
    
def get_current_status_card():
    card_content_confirmed = [
            html.Div(
                [	html.H6("Confirmed",className="text-center"),
                    html.Div(
                        "{0:n}".format(get_daily_data()["Daily Confirmed"].values[0]),
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
                        "{0:n}".format(get_daily_data()["Daily Recovered"].values[0]),
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
                        "{0:n}".format(get_daily_data()["Daily Deceased"].values[0]),
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


def get_overall_status_card():
    
    return html.Div(children=[
    	html.Div([html.H6("Total Confirmed", className="text-danger text-center"),
           		html.P("{0:n}".format(get_total_confirmed_data()),className="text-danger text-center",)],
           		className="mini_container",),

    	html.Div([html.H6("Active Cases", className="text-info text-center"),
           		html.P("{0:n}".format(get_total_active_data()),className="text-info text-center")],
           		className="mini_container",),

    	html.Div([html.H6("Total Recovered", className="text-success text-center"),
           		html.P("{0:n}".format(get_total_recovered_data()),className="text-success text-center")],
           		className="mini_container",),

    	html.Div([html.H6("Total Deceased",className="text-muted text-center"),
           		html.P("{0:n}".format(get_total_death_data()),className="text-muted text-center")],
           		className="mini_container",),
   		],className="two columns")


def get_tests_vs_positive_data():
    daily_test_url = 'https://api.covid19india.org/csv/latest/tested_numbers_icmr_data.csv'
    daily_test_data = pd.read_csv (daily_test_url)
    sample_daily_test_data = daily_test_data.tail(14)
    sample_case_data = case_file.tail(14)
    positivity_rate = []
    no_of_tests = []
    counter = 0
    for index, row in sample_case_data.iterrows():
        no_of_tests.append(sample_daily_test_data.values[counter][6])
        if sample_daily_test_data.values[counter][6] is not 'Nan' :
            positivity_rate.append(round((sample_case_data.values[counter][1]/int(sample_daily_test_data.values[counter][6])*100),2))
        counter += 1
    graph_data = {'Date': sample_case_data['Date'],
        'Number Of Tests': no_of_tests,
        'Positive': sample_case_data['Daily Confirmed'],
        'Positivity Rate': positivity_rate
        }

    df = pd.DataFrame (graph_data, columns = ['Date','Number Of Tests','Positive','Positivity Rate'])
    return df

def get_tests_vs_positive_graph():
   # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    df = get_tests_vs_positive_data()
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
def get_death_data():
    state_wise_deceased_data = state_wise_daily_data[state_wise_daily_data['Status'] == 'Deceased']
    state_wise_deceased_data = state_wise_deceased_data.drop(['TT','DD'], axis=1)
    state_wise_deceased_data = state_wise_deceased_data.reset_index()
    return state_wise_deceased_data

def get_confirmed_data():
    state_wise_confirmed_data = state_wise_daily_data[state_wise_daily_data['Status'] == 'Confirmed']
    state_wise_confirmed_data = state_wise_confirmed_data.drop(['TT','DD'], axis=1)
    state_wise_confirmed_data = state_wise_confirmed_data.reset_index()
    return state_wise_confirmed_data
    
def get_state_code_list():
    state_wise_url = 'https://api.covid19india.org/csv/latest/state_wise.csv'
    state_wise_data = pd.read_csv(state_wise_url)
    state_wise_data.replace('Dadra and Nagar Haveli and Daman and Diu', 'DNHDD',inplace=True)
    state_code_list = state_wise_data[['State','State_code']][1:]
    # index_pos = int(state_code_list[state_code_list['State_code']=='DN'].index[0])
    # state_code_list.at[index_pos,'State'] = 'DN & DU'
    # state_code_list.loc[state_code_list['State_code']=='DN']['State']
    return state_code_list

def get_death_rate_data():
    state_wise_deceased_data = get_death_data()
    state_wise_confirmed_data = get_confirmed_data()
    #number of biweekly chunks required
    n = int(state_wise_deceased_data.shape[0]/14)
    data = {'Days Interval': [0]
       }
    data_set = pd.DataFrame(data) 
    state_code_list = get_state_code_list()
    for i in state_code_list['State_code']:
        data_set[i] = 'Nan'
    # a period of 2 weeks
    lower_limit = 0
    upper_limit = 13
    state_wise_death_rate = {}
    for i in range(n+1):
        row = [upper_limit + 1]
        total_confirmed_cases_biweekly = state_wise_confirmed_data.loc[lower_limit:upper_limit].sum()
        total_deceased_cases_biweekly = state_wise_deceased_data.loc[lower_limit:upper_limit].sum()
        for i in state_code_list['State_code']:
            if total_confirmed_cases_biweekly[i] == 0:
                state_wise_death_rate[i] = 0
            else:
                state_wise_death_rate[i] = round((total_deceased_cases_biweekly[i]/total_confirmed_cases_biweekly[i])*100,2)
            row.append(state_wise_death_rate[i])
        data_set.loc[len(data_set)] = row
        lower_limit =upper_limit + 1
        upper_limit += 14
    row = [upper_limit + 1]
    row += ['Nan']*37
    data_set.loc[len(data_set)] = row
    return data_set

def get_death_rate_graph():
    data = []
    state_code_list = get_state_code_list()
    data_set = get_death_rate_data()
    for i in state_code_list['State_code']:
        if i == 'DN':
        	index_pos = int(state_code_list[state_code_list['State_code']=='DN'].index[0])
        	state_code_list.at[index_pos,'State']= 'DNHDD'
        data.append(go.Scatter(x=data_set['Days Interval'], y=data_set[i], mode="lines",
                               name=state_code_list[state_code_list['State_code']==i]['State'].values[0]))

    fig = go.Figure(data=data)

    # Suffix y-axis tick labels with % sign
    fig.update_yaxes(ticksuffix="%")
    fig.update_xaxes(tick0=0, dtick=14)

    fig.update_layout(
        title="Death Rate - State wise overview",
        xaxis={"fixedrange": True},
        # {
        #     'text': "Death Rate - State wise overview",
        #     'y':0.9,
        #     'x':1,
        #     'xanchor': 'center',
        #     'yanchor': 'top'},
        xaxis_title="No Of Days",
        yaxis_title="Death rate",
        legend_title="States",
        hovermode = "x",
        # font=dict(
        #     family="Courier New, monospace",
        #     size=15,
        #     color="RebeccaPurple"
        # )

    )

    return fig

def get_tpm_cpm_data():
    # last_day_1 = (date.today()  - timedelta(days = 1)).strftime('%d-%m-%Y')
    # test_data1 = test_data[test_data['Updated On'] < last_day_1]
    # #test_data = test_data[test_data['Updated On'] < last_day_1]
    # test_data1['Case Per Million'] = round((test_data1['Positive']/(test_data1['Population NCP 2019 Projection']/1000000)))
    # test_data1['Test Per Million'] = round((test_data1['Total Tested']/(test_data1['Population NCP 2019 Projection']/1000000)))
    test_data.drop(test_data[test_data['Updated On'] == date.today().strftime('%d/%m/%Y')].index, inplace = True)
    test_data.replace('Dadra and Nagar Haveli and Daman and Diu', 'DNHDD',inplace=True) 
    group_data = test_data.groupby('State')
    population_dict = get_state_population(group_data)
    return group_data, population_dict

def get_state_population(group_data):
	population_dict = {}
	for i in group_data.groups.keys():
		population_dict[i] = test_data[test_data['State']==i]['Population NCP 2019 Projection'].values[0]
	return population_dict

def get_tpm_cpm_graph():
    data = []
    state_code_list = get_state_code_list()
    group_data, population_dict = get_tpm_cpm_data()
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

def get_tpm_cpm_table():
    #table
    table_data = {'State': {},
                  'Test Per Million':{},
                  'Case Per Million':{}
           }
    data_table = pd.DataFrame(table_data) 
    group_data,population_dict = get_tpm_cpm_data()
    for i in group_data.groups.keys():
        row = [i,round(group_data.get_group(i)['Total Tested']/(population_dict[i]/1000000)).tail(1).values[0],
          round(group_data.get_group(i)['Positive']/(population_dict[i]/1000000)).tail(1).values[0]]
        data_table.loc[len(data_table)] = row
    return data_table
def get_tpm_cpm_combined():
    
    card = dbc.Card(
        [
            dbc.CardHeader(
                dbc.Tabs(
                    [
                       dcc.Tab(label='Graph', children=[
                                dcc.Graph(
                                    figure = get_tpm_cpm_graph(),
                                  config={'displayModeBar': False})
                            ]),
                        dcc.Tab(label='Table', children=[
                                dbc.Table.from_dataframe(get_tpm_cpm_table(), striped=True, bordered=True, hover=True)
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

def get_test_per_positive_data():
    last_updated_date = state_wise_daily_data.tail(1)['Date']
    date_time_obj = datetime. strptime(last_updated_date.values[0], '%d-%b-%y')
    last_updated_date = (date_time_obj + timedelta(days = 1)).strftime('%d-%b-%y')
    #filtered_data = test_data[test_data['Updated On'] <= last_updated_date][['State','Tests per positive case']]
    test_data.drop(test_data[test_data['Updated On'] == date.today().strftime('%d/%m/%Y')].index, inplace = True)
    test_data['Test Positivity'] = round((test_data['Total Tested']/test_data['Positive'])*100,2)
    test_per_positive_data = test_data.groupby('State')
    return test_per_positive_data

def get_fatality_state_wise_data():
    table_data = {
        'State':{},
        'Fatality Rate':{},
        'Test Per Positive Case':{}
    }
    data_table = pd.DataFrame(table_data)
    cum_deceased_data = get_death_data().cumsum()
    cum_confirmed_data = get_confirmed_data().cumsum()
    test_per_positive_data = get_test_per_positive_data()
    state_code_list = get_state_code_list()
    previous_day = (date.today()  - timedelta(days = 1)).strftime('%d/%m/%Y')
    for i in test_per_positive_data.groups.keys():
        test_per_confirmed = test_per_positive_data.get_group(i).tail(30)
        if i == 'Dadra and Nager Haveli and Daman and Diu':
            i = 'DN & DU'
        state_code = state_code_list[state_code_list['State']==i]['State_code'].values[0]
        fatality_rate = ((cum_deceased_data[state_code]/cum_confirmed_data[state_code])*100).tail(30)
        #table population
        test_per_confirmed_latest = test_per_confirmed[test_per_confirmed['Updated On']==previous_day]['Test Positivity']
        fatality_rate_latest = round(fatality_rate.tail(1).values[0],2)
        row = [i,fatality_rate_latest,test_per_confirmed_latest]
        data_table.loc[len(data_table)] = row
        data_table.sort_values(by=['Fatality Rate'],ascending=False,inplace=True)
    return data_table

def get_fatality_state_wise_graph():
    data_table = get_fatality_state_wise_data()
    modeBarButtons = [['toImage']]
    fig = px.bar(data_table, x='State', y='Fatality Rate',width=500,
    	color='Fatality Rate', color_continuous_scale=px.colors.sequential.YlOrRd,
    	)
    fig.update_xaxes(tickangle=45,)
    return fig, data_table
    

def get_fatality_test_per_positive_graph():
    #table
    table_data = {'State': {},
                  'Fatality Rate':{},
                  'Test Per Positive Case':{}
           }
    data_table = pd.DataFrame(table_data)
    data=[]
    # fig = make_subplots(
    # rows=1, cols=2,
    # vertical_spacing=0.3,
    # specs=[[{"type": "scatter"},{"type": "table"}]]
    # )
    cum_deceased_data = get_death_data().cumsum()
    cum_confirmed_data = get_confirmed_data().cumsum()
    test_per_positive_data = get_test_per_positive_data()
    state_code_list = get_state_code_list()
    previous_day = (date.today()  - timedelta(days = 1)).strftime('%d/%m/%Y')
    for i in test_per_positive_data.groups.keys():
        test_per_confirmed = test_per_positive_data.get_group(i).tail(30)
        if i == 'Dadra and Nager Haveli and Daman and Diu':
            i = 'DN & DU'
        state_code = state_code_list[state_code_list['State']==i]['State_code'].values[0]
        fatality_rate = ((cum_deceased_data[state_code]/cum_confirmed_data[state_code])*100).tail(30)
        data.append(go.Scatter(x=test_per_confirmed['Test Positivity'], 
                           y=fatality_rate, mode="lines",
                           name=i))
        #table population
        test_per_confirmed_latest = test_per_confirmed[test_per_confirmed['Updated On']==previous_day]['Test Positivity']
        #print(test_per_confirmed_latest)
        fatality_rate_latest = round(fatality_rate.tail(1).values[0],2)
        row = [i,fatality_rate_latest,test_per_confirmed_latest]
        data_table.loc[len(data_table)] = row

    # fig = go.Figure(data=data)

    # fig.update_layout(
    #     title={
    #         'text': "Case Fatality Rate v/s Test Per Positive Case",
    #         'y':0.9,
    #         'x':0.3,
    #         'xanchor': 'center',
    #         'yanchor': 'top'},
    #     xaxis={"fixedrange": True},
    #     xaxis_title="Test per positive case",
    #     yaxis_title="Case fatality rate",
    #     legend_title="States",

    # )
    
    # fig.add_trace(go.Table(
    #     header=dict(
    #         values=data_table.columns,
    #         font=dict(size=10),
    #         align="left"
    #     ),
    #     cells=dict(
    #         values=[data_table[k].tolist() for k in data_table.columns],
    #         align = "left")
    # ),row=1,col=2
    # )
    return data_table

def get_fatality_graph():
	graph, table = get_fatality_state_wise_graph()
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

nav = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("tpm-cpm", href="#tpm-cpm",external_link=True)),
        dbc.DropdownMenu(
            children=[
              	#dbc.NavLink("Death Rate", href="#death-rate", id="death-rate-link",external_link=True),
                #dbc.NavLink("Fatality Rate", href="#fatality", id="fatality-link",external_link=True),
                #dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("tpm-cpm", href="#tpm-cpm",external_link=True),
                # dbc.DropdownMenuItem("tpm", 
                # 	href=[dbc.NavLink("Fatality Rate", href="#fatality", id="fatality-link",external_link=True)],
                # 	external_link=True),
                #dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="NavbarSimple",
    brand_href="#",
    color="primary",
    dark=True,
)

section_list = dbc.Nav(
            [
                dbc.NavLink("Covid Status", href="#covid-status", id="covid-status-link",external_link=True),
                dbc.NavLink("Test Positivity", href="#test-positivity", id="test-positivity-link",external_link=True),
                dbc.NavLink("Test Efficiency", href="#tpm-cpm", id="tpm-cpm-link",external_link=True),
                dbc.NavLink("Death Rate", href="#death-rate", id="death-rate-link",external_link=True),
                dbc.NavLink("Fatality Rate", href="#fatality", id="fatality-link",external_link=True),
            ],
             # horizontal=True,
             # pills=True,
             fill=True,
             style={"font-size":"22px"}
        )


collapse = html.Div(
    [
        dbc.Button(
            "Explore",
            id="left",
            #className="mb-3",
            color="primary",
        ),
        dbc.Collapse(
            section_list,
            id="left-collapse",
            #style={"width":"20px"}
        ),
    ]
)

navbar = dbc.NavbarSimple(
    children=[
       collapse
    ],
    #brand="NavbarSimple",
    brand_href="#",
    color="lightgrey",
    dark=True,
)

# @app.callback(
#     Output("left-collapse", "is_open"),
#     [Input("left", "n_clicks")],
#     [State("left-collapse", "is_open")],
# )
# def toggle_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open

sidebar_header = dbc.Row(
    [
        dbc.Col(html.H2("Explore", className="display-4")),
        dbc.Col(
            [
                
                html.Button(
                    # use the Bootstrap navbar-toggler classes to style
                    html.Span(className="navbar-toggler-icon"),
                    
                    # the navbar-toggler classes don't set color
                    style={
                        "color": "#ffb3b3",
                        "border-color": "rgba(0,0,0,.1)",
                        "background-color":"#cccccc",
                    },
                    id="sidebar-toggle",
                ),
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
                dbc.NavLink("Test Positivity", href="#test-positivity", id="test-positivity-link",external_link=True),
                dbc.NavLink("Test Efficiency", href="#tpm-cpm", id="tpm-cpm-link",external_link=True),
                dbc.NavLink("Death Rate", href="#death-rate", id="death-rate-link",external_link=True),
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
	    dbc.Alert([html.B([
	    	html.P(["Someone is dying in every",
	    		html.Span(get_death_rate(),style={"font-size":"50px","padding-left":"5px","padding-right":"5px"}),"in India!",
	    		]),
	    	],className="text-danger",style={"font-size":"25px"}),], color="danger",
	    className="p-5 text-center",style={"font-size":"large","border-radius": "7px"}),
	    html.Div(get_current_status_card(),id="status",),
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
	   	dbc.Col(html.Div(get_overall_status_card()),width="60%"),
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

	   	html.Div([
	   		
	   		 dbc.Card(
        [
        dbc.CardHeader("Test Positivity",style={"font-size":"30px"}),
        dbc.CardBody(
            [
               	dbc.Row([
	   			dbc.Col(dcc.Graph(figure = get_tests_vs_positive_graph(),
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
	   		dbc.Col( get_tpm_cpm_combined(),
	           ),
	   		]),
            ]
        ),
    ],)], id="tpm-cpm",),
	        

	    html.Div( dbc.Card(
        [
        dbc.CardHeader("Death Rate",style={"font-size":"30px"}),
        dbc.CardBody(
            [
               	dbc.Row([
	   			dbc.Col(dcc.Graph(figure = get_death_rate_graph(),
	                              config={'displayModeBar': False}),
	   			),
	            dbc.Col(html.Div(html.P("Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.")
	   		,className="text_style"),className="center-container", width="40%")
	            ])
            ]
        ),
    ],),id="death-rate",className="pretty_container"),
	    
	    html.Div([
	    	html.H2("Fatality Rate",className="heading_style"),
	    	html.Div(get_fatality_graph())
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


# @app.callback(
#     Output("collapse", "is_open"),
#     [Input("navbar-toggle", "n_clicks")],
#     [State("collapse", "is_open")],
# )
# def toggle_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open

app.layout = html.Div([
	    #dcc.Location(id='url', refresh=True),
		#html.Div(nav),
		sidebar,
    	content,   
],className="wrapper",
)

if __name__ == '__main__':
    app.run_server(debug=True)
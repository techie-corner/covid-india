import pandas as pd
import plotly.graph_objects as go 
from plotly.subplots import make_subplots

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_html_components as html

from datetime import date 
from datetime import datetime
from datetime import timedelta

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server



SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "8rem",
    "padding": "2rem 1rem",
}

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
    minutes = int(death_rate/60)
    seconds = int(round(death_rate%60,0))
    return 'Someone is dying in every {} minutes and {} seconds in India!'.format(minutes, seconds)

def get_covid_status_graph():
    # Create traces
    fig = go.Figure()
    fig.layout.xaxis.zeroline = False
    fig.layout.yaxis.zeroline = False
    #Total Confirmed cases
    fig.add_trace(go.Scatter(x=case_file.Date, y=case_file["Total Confirmed"],
                    mode='lines',
                    line_color='tomato',
                    name='Total Confirmed'))

    #Total Active cases
    fig.add_trace(go.Scatter(x=case_file.Date, y=case_file["Total Recovered"] + case_file["Total Deceased"],
                    mode='lines',
                    fill='tonexty',
                    name='Total Active',
                    fillcolor = 'thistle',
                    line_color='gold'))

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
    line_color='darkred'
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
    line_color='palegreen'
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
    title = "Covid Status in India",
    autosize=True,
   # width=800,
   # height=500,
    hovermode="x unified",
    margin=dict(
        l=50,
        r=20,
        b=10,
        t=50,
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
            dbc.CardHeader(html.H5("Confirmed"), className="bg-danger text-center"),
            dbc.CardBody(
                [
                    html.P(
                        "{0:n}".format(get_daily_data()["Daily Confirmed"].values[0]),
                        className="card-text text-center",
                    ),
                ],className="w-10"
            )
        ]
    card_content_recovered = [
            dbc.CardHeader(html.H5("Recovered"),className="bg-success text-center"),
            dbc.CardBody(
                [
                    html.P(
                        "{0:n}".format(get_daily_data()["Daily Recovered"].values[0]),
                        className="card-text text-center",
                    ),
                ],className="w-10"
            )
        ]
    card_content_deceased = [
            dbc.CardHeader(html.H5("Deceased"), className="bg-secondary text-center"),
            dbc.CardBody(
                [
                    html.P(
                        "{0:n}".format(get_daily_data()["Daily Deceased"].values[0]),
                        className="card-text text-center",
                    ),
                ],className="w-10"
            )
        ]
    
    current_status_arrange = [dbc.Row(
        [
            dbc.Col(dbc.Card(card_content_confirmed, color="danger", outline = True,)),
            dbc.Col(dbc.Card(card_content_recovered, color="success", outline = True,)),
            dbc.Col(dbc.Card(card_content_deceased, color="secondary",outline = True,)),
        ],
        className="mb-4"
    ),         
    ]
    card_current_status = [
            dbc.CardBody(
                [
                    html.P(
                       current_status_arrange
                    ),
                ]
            ),

            ]
        
    return card_current_status

def get_overall_status_card():
    
    return html.Div(children=[
        dbc.Row([
            
            dbc.Col(html.Div([
           html.H6("Total Confirmed", className="text-danger text-center"),
           html.P("{0:n}".format(get_total_confirmed_data()),className="text-danger text-center",)
        ],style=mini_container,)),
            
            dbc.Col(html.Div([
           html.H6("Active Cases", className="text-info text-center"),
           html.P("{0:n}".format(get_total_death_data()),className="text-info text-center")
        ],style=mini_container))
        ]),
         dbc.Row([
             dbc.Col(html.Div([
           html.H6("Total Recovered",className="text-success text-center"),
           html.P("{0:n}".format(get_total_death_data()),className="text-success text-center")
        ],style=mini_container),),
             
            dbc.Col(html.Div([
           html.H6("Total Deceased",className="text-muted text-center"),
           html.P("{0:n}".format(get_total_death_data()),className="text-muted text-center")
        ],style=mini_container),)
             
        ])
     ])



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
        marker={'color': 'yellow'}
    ), secondary_y=False)

    fig.add_trace(go.Bar(
        x=df["Date"], 
        y=df['Number Of Tests'],
        name="Number of tests",
        marker={'color': 'blue'}
    ), secondary_y=False)


    # Add traces
    fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Positivity Rate'],
    mode="lines",
    name="Positivity Rate (in %)",
    line_color='tomato'
    ), secondary_y=True)

    # Change the bar mode
    fig.update_layout(barmode='stack',title = "Daily Tests vs Positive Cases",
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
    state_code_list = state_wise_data[['State','State_code']][1:]
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
        data.append(go.Scatter(x=data_set['Days Interval'], y=data_set[i], mode="lines",
                               name=state_code_list[state_code_list['State_code']==i]['State'].values[0]))

    fig = go.Figure(data=data)

    # Suffix y-axis tick labels with % sign
    fig.update_yaxes(ticksuffix="%")
    fig.update_xaxes(tick0=0, dtick=14)

    fig.update_layout(
        title={
            'text': "Death Rate - State wise overview",
            'y':0.9,
            'x':0.3,
            'xanchor': 'center',
            'yanchor': 'top'},

        xaxis_title="No Of Days",
        yaxis_title="Death rate",
        legend_title="States",
        hovermode = "x",
        font=dict(
            family="Courier New, monospace",
            size=15,
            color="RebeccaPurple"
        )
    )

    return fig

def get_tpm_cpm_data():
    last_day_1 = (date.today()  - timedelta(days = 1)).strftime('%d-%m-%Y')
    test_data1 = test_data[test_data['Updated On'] < last_day_1]
    #test_data = test_data[test_data['Updated On'] < last_day_1]
    test_data1['Case Per Million'] = round((test_data1['Positive']/(test_data1['Population NCP 2019 Projection']/1000000)))
    group_data = test_data1.groupby('State')
    return group_data

def get_tpm_cpm_graph():
    data = []
    group_data = get_tpm_cpm_data()
    for i in group_data.groups.keys():

        data.append(go.Scatter(x=group_data.get_group(i)['Case Per Million'], 
                               y=group_data.get_group(i)['Tests per million'], mode="lines",
                               name=i))

    fig = go.Figure(data=data)


    fig.update_layout(
        title={
            'text': "Test Per Million v/s Case Per Million",
            'y':0.9,
            'x':0.3,
            'xanchor': 'center',
            'yanchor': 'top'},

        xaxis_title="Case Per Million",
        yaxis_title="Test per million",
        legend_title="States",
        font=dict(
            family="Courier New, monospace",
            size=15,
            color="RebeccaPurple"
        )
    )
    
    return fig

def get_tpm_cpm_table():
    #table
    table_data = {'State': {},
                  'Test Per Million':{},
                  'Case Per Million':{}
           }
    data_table = pd.DataFrame(table_data) 
    group_data = get_tpm_cpm_data()
    for i in group_data.groups.keys():
        row = [i,group_data.get_group(i)['Tests per million'].tail(1).values[0],group_data.get_group(i)['Case Per Million'].tail(1).values[0]]
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
                    id="card-tabs",
                    card=True,
                    
                )
            ),
            dbc.CardBody(html.P(id="card-content", className="card-text")),
        ]
    )
    
    return card

def get_test_per_positive_data():
    last_updated_date = state_wise_daily_data.tail(1)['Date']
    date_time_obj = datetime. strptime(last_updated_date.values[0], '%d-%b-%y')
    last_updated_date = (date_time_obj + timedelta(days = 1)).strftime('%d-%b-%y')
    filtered_data = test_data[test_data['Updated On'] <= last_updated_date][['State','Tests per positive case']]
    test_per_positive_data = filtered_data.groupby('State')
    return test_per_positive_data

def get_fatality_test_per_positive_graph():
    #table
    table_data = {'State': {},
                  'Fatality Rate':{},
                  'Test Per Positive Case':{}
           }
    data_table = pd.DataFrame(table_data)
    data=[]
    fig = make_subplots(
    rows=1, cols=2,
    vertical_spacing=0.3,
    specs=[[{"type": "scatter"},{"type": "table"}]]
    )
    cum_deceased_data = get_death_data().cumsum()
    cum_confirmed_data = get_confirmed_data().cumsum()
    test_per_positive_data = get_test_per_positive_data()
    state_code_list = get_state_code_list()
    for i in test_per_positive_data.groups.keys():
        test_per_confirmed = test_per_positive_data.get_group(i).tail(30)
        state_code = state_code_list[state_code_list['State']==i]['State_code'].values[0]
        fatality_rate = ((cum_deceased_data[state_code]/cum_confirmed_data[state_code])*100).tail(30)
        fig.add_trace(go.Scatter(x=test_per_confirmed['Tests per positive case'], 
                           y=fatality_rate, mode="lines",
                           name=i),row=1,col=1)
        #table population
        test_per_confirmed_latest = test_per_confirmed.tail(1).values[0][1]
        #print(test_per_confirmed_latest)
        fatality_rate_latest = round(fatality_rate.tail(1).values[0],2)
        row = [i,fatality_rate_latest,test_per_confirmed_latest]
        data_table.loc[len(data_table)] = row

    fig.update_yaxes(ticksuffix="%")

    fig.update_layout(
        title={
            'text': "Case Fatality Rate v/s Test Per Positive Case",
            'y':0.9,
            'x':0.3,
            'xanchor': 'center',
            'yanchor': 'top'},

        xaxis_title="Test per positive case",
        yaxis_title="Case fatality rate",
        legend_title="States",

    )
    
    fig.add_trace(go.Table(
        header=dict(
            values=data_table.columns,
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[data_table[k].tolist() for k in data_table.columns],
            align = "left")
    ),row=1,col=2
    )
    return fig

sidebar = html.Div(
    [
        html.H2("Explore", className="display-4"),
        html.Hr(),
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
        ),
    ],
    style = SIDEBAR_STYLE
)



app.layout = dbc.Container(children=[dcc.Location(id="url"),
    html.Div([
    dbc.Alert(get_death_rate(), color="danger",style={'text-align':'center','width':'100'},
    className="p-5"),
    html.Div(get_current_status_card(),id="status"),
    html.Div(dbc.Row(
        [
            dbc.Col(get_overall_status_card(),width = 4,),
            dbc.Col(dcc.Graph(figure = get_covid_status_graph(),
                   config={'displayModeBar': False,}))
        ],
        className="mb-4",
    ),id = "covid-status"),
    html.Div(
             dbc.Row(
        [
            dbc.Col(dcc.Graph(figure = get_tests_vs_positive_graph(),
                              config={'displayModeBar': False}),),
        ],
        className="mb-4",
    ), id = 'test-positivity'),
        
    html.Div([dbc.Row(
             dbc.Col(html.H3("Test per million vs Case per million"))),
              
                    dbc.Row(
        [
            dbc.Col(get_tpm_cpm_combined(),),
        ],
        className="mb-5,h-50",
    )],id="tpm-cpm"),
        
    html.Div(
                    dbc.Row(
        [           
            dbc.Col(dcc.Graph(figure = get_death_rate_graph(),
                              config={'displayModeBar': False},animate=True),),
        ],
        className="mb-4",
    ),id="death-rate"),
    
    html.Div(
               dbc.Row(
        [
            dbc.Col(dcc.Graph(figure = get_fatality_test_per_positive_graph(),
                              config={'displayModeBar': False},animate=True)),
        ],
        className="mb-4",
    ),id="fatality"
    )],id="content",style=CONTENT_STYLE),
    sidebar,]

)
if __name__ == '__main__':
    app.run_server(debug=True)
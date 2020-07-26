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

target_url = 'https://api.covid19india.org/csv/latest/case_time_series.csv'
case_file = pd.read_csv (target_url)
test_file_location = "https://api.covid19india.org/csv/latest/statewise_tested_numbers_data.csv"
test_data = pd.read_csv(test_file_location)
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
        r=50,
        b=10,
        t=100,
        pad=10),

    )
    
    return fig


def get_daily_data():
    daily_data = case_file.tail(1)
    return daily_data[["Daily Confirmed","Daily Recovered","Daily Deceased"]]

def get_status_cards():
    card_content_confirmed = [
        dbc.CardHeader("Confirmed"),
        dbc.CardBody(
            [
                html.P(
                    get_daily_data()["Daily Confirmed"].values[0],
                    className="card-text",
                ),
            ]
        ),
    ]
    card_content_recovered = [
        dbc.CardHeader("Recovered"),
        dbc.CardBody(
            [
                html.P(
                    get_daily_data()["Daily Recovered"].values[0],
                    className="card-text",
                ),
            ]
        ),
    ]
    card_content_deceased = [
        dbc.CardHeader("Deceased"),
        dbc.CardBody(
            [
                html.P(
                    get_daily_data()["Daily Deceased"].values[0],
                    className="card-text",
                ),
            ]
        ),
    ]
    status_cards = dbc.Row(
        [
            dbc.Col(dbc.Card(card_content_confirmed, color="warning", inverse=True)),
            dbc.Col(dbc.Card(card_content_recovered, color="success",  inverse=True)),
            dbc.Col(dbc.Card(card_content_deceased, color="danger",  inverse=True)),
        ],
        className="mb-4",
    )
    return status_cards
def get_tests_vs_positive_data():
    last_day_1 = (date.today()  - timedelta(days = 1)).strftime('%d/%m/%Y') 
    last_day_2 = (date.today()  - timedelta(days = 2)).strftime('%d/%m/%Y') 
    filtered_data_1 = test_data[test_data['Updated On'] == last_day_1]
    filtered_data_2 = test_data[test_data['Updated On'] == last_day_2]
    state_list = []
    no_of_tests = []
    positive_cases = []
    positivity_rate = []
    df_columns = filtered_data_1.values
    counter = 0
    for index, row in filtered_data_1.iterrows():
        state_list.append(row["State"])
        no_of_tests.append((row["Total Tested"] - filtered_data_2[filtered_data_2['State'] == row['State']]["Total Tested"].values[0]))
        positive_cases.append(row["Positive"] - filtered_data_2[filtered_data_2['State'] == row['State']]["Positive"].values[0])
        positivity_rate.append((positive_cases[counter]/no_of_tests[counter])*100)
        counter += 1
    graph_data = {'State': state_list,
        'Total Tested': no_of_tests,
        'Positive': positive_cases,
        'Positivity Rate': positivity_rate
        }

    df = pd.DataFrame (graph_data, columns = ['State','Total Tested','Positive','Positivity Rate'])
    df = df.sort_values(by=['Total Tested'])
    return df

def get_tests_vs_positive_graph():
    # Create figure with secondary y-axis
    df = get_tests_vs_positive_data()
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    
    fig.add_trace(go.Bar(
        x=df['State'], 
        y=df['Positive'],
        name="Positive Cases",
        marker={'color': 'yellow'}
    ), secondary_y=False)

    
    fig.add_trace(go.Bar(
        x=df['State'], 
        y=df['Total Tested'],
        name="Daily Tests",
        marker={'color': 'blue'}
    ), secondary_y=False)



    # Add traces
    fig.add_trace(go.Scatter(
    x=df['State'],
    y=df['Positivity Rate'],
    mode="lines",
    name="Positivity Rate",
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
         hovermode="x unified")
    return fig
app.layout = dbc.Container(children=[
    dbc.Alert(get_death_rate(), color="danger",style={'text-align':'center','width':'100'},
    className="p-5"),
    html.Div(get_status_cards()),
     html.Div([dbc.Row(
        [
            dbc.Col(dcc.Graph(figure = get_covid_status_graph(),
                   config={'displayModeBar': False}),)
        ],
        className="mb-4",
    ),
             dbc.Row(
        [
            dbc.Col(dcc.Graph(figure = get_tests_vs_positive_graph(),
                              config={'displayModeBar': False}),),
        ],
        className="mb-4",
    )
             ])
]
)
if __name__ == '__main__':
    app.run_server(debug=True)
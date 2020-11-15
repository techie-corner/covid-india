#utility functions for death rate component

data_set = []
death_confirmed_data = {}

def get_death_confirmed_data(data_set):
    state_wise_daily_data = data_set['state_wise_daily_data'].drop(['TT','DD'], axis=1)

    state_wise_deceased_data = state_wise_daily_data[state_wise_daily_data['Status'] == 'Deceased']
    state_wise_deceased_data = state_wise_deceased_data.reset_index()

    state_wise_confirmed_data = state_wise_daily_data[state_wise_daily_data['Status'] == 'Confirmed']
    state_wise_confirmed_data = state_wise_confirmed_data.reset_index()

    death_confirmed_data = {
    "state_wise_deceased_data" : state_wise_deceased_data,
    "state_wise_confirmed_data" : state_wise_confirmed_data
    }

    return death_confirmed_data

def get_no_of_chunks(state_wise_deceased_data):

	return int(state_wise_deceased_data.shape[0]/14)

def get_death_rate_data(data_set):

    state_wise_deceased_data = death_confirmed_data['state_wise_deceased_data']
    state_wise_confirmed_data = death_confirmed_data['state_wise_confirmed_data']

    #number of biweekly chunks required
    n = get_no_of_chunks(state_wise_deceased_data)

    #create new customised data frame
    data = {'Days Interval': [0]
       }
       
    death_rate_data_set = pd.DataFrame(data) 
    state_code_list = get_state_code_list()
    for i in state_code_list['State_code']:
        death_rate_data_set[i] = 'Nan'

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
        death_rate_data_set.loc[len(death_rate_data_set)] = row
        upper_limit += 14
    row = [upper_limit + 1]
    row += ['Nan']*37
    death_rate_data_set.loc[len(death_rate_data_set)] = row
    return death_rate_data_set

#for backup
# def get_death_rate_graph(data_set):
#     data = []
#     data_set = death_rate.get_death_rate_data(data_set)
#     for i in state_code_list['State_code']:
#         if i == 'DN':
#         	index_pos = int(state_code_list[state_code_list['State_code']=='DN'].index[0])
#         	state_code_list.at[index_pos,'State']= 'DNHDD'
#         data.append(go.Scatter(x=data_set['Days Interval'], y=data_set[i], mode="lines",
#                                name=state_code_list[state_code_list['State_code']==i]['State'].values[0]))

#     fig = go.Figure(data=data)

#     # Suffix y-axis tick labels with % sign
#     fig.update_yaxes(ticksuffix="%")
#     fig.update_xaxes(tick0=0, dtick=14)

#     fig.update_layout(
#         title="Death Rate - State wise overview",
#         xaxis={"fixedrange": True},
#         # {
#         #     'text': "Death Rate - State wise overview",
#         #     'y':0.9,
#         #     'x':1,
#         #     'xanchor': 'center',
#         #     'yanchor': 'top'},
#         xaxis_title="No Of Days",
#         yaxis_title="Death rate",
#         legend_title="States",
#         hovermode = "x",
#         # font=dict(
#         #     family="Courier New, monospace",
#         #     size=15,
#         #     color="RebeccaPurple"
#         # )

#     )

#     return fig

if __name__ == '__main__': 
	get_death_confirmed_data(data_set)
	get_no_of_chunks(data_set)
	get_death_rate_data(data_set)

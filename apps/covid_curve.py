#utility functions for covid curve component

data_set = []

def get_cumulative_status_data(data_set):
    case_time_series_data = data_set['case_time_series_data']
    cumulative_data = case_time_series_data.tail(1)
    return {
    "Total Confirmed": cumulative_data["Total Confirmed"].values[0],
    "Total Recovered": cumulative_data["Total Recovered"].values[0],
    "Total Deceased": cumulative_data["Total Deceased"].values[0],
    "Active": cumulative_data["Total Confirmed"].values[0] - (cumulative_data["Total Recovered"].values[0] + cumulative_data["Total Deceased"].values[0])
    }

def get_state_wise_data(data_set, state):
	states_data = data_set['states_data']
	if state == 'DNHDD':
		state = 'Dadra and Nagar Haveli and Daman and Diu'
	return states_data[states_data['State']== state]



if __name__ == '__main__': 
	get_cumulative_status_data(data_set)
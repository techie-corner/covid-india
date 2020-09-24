#common utility functions

data_set = []

def get_state_code_list(data_set):
    state_wise_data = data_set['state_wise_data']
    state_wise_data.replace('Dadra and Nagar Haveli and Daman and Diu', 'DNHDD',inplace=True)
    state_code_list = state_wise_data[['State','State_code']][1:]
    return state_code_list

def get_state_code(data_set, state):
	state_code_list = get_state_code_list(data_set)
	return state_code_list[state_code_list['State'] == state]['State_code'].values[0]

if __name__ == '__main__': 
	get_state_code_list(data_set)

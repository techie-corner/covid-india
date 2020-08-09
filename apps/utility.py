#common utility functions

data_set = []

def get_state_code_list(data_set):
    state_wise_data = data_set['state_wise_data']
    state_wise_data.replace('Dadra and Nagar Haveli and Daman and Diu', 'DNHDD',inplace=True)
    state_code_list = state_wise_data[['State','State_code']][1:]
    return state_code_list

if __name__ == '__main__': 
	get_state_code_list(data_set)

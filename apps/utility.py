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

def get_state_population():

	population_dict = {'Andaman and Nicobar Islands' : 397000,
						'Andhra Pradesh' : 52221000,
						'Arunachal Pradesh'	: 1504000,
						'Assam'	: 34293000,
						'Bihar'	: 119520000,
						'Chandigarh' : 1179000,
						'Chhattisgarh' : 28724000,
						'DNHDD' : 959000,
						'Delhi' : 19814000,
						'Goa' : 1540000,
						'Gujarat' : 67936000,
						'Haryana' : 28672000,
						'Himachal Pradesh' : 7300000,
						'Jammu and Kashmir' : 13203000,
						'Jharkhand' : 37403000,
						'Karnataka' : 65798000,
						'Kerala' : 35125000,
						'Ladakh' : 293000,
						'Lakshadweep' : 68000,
						'Madhya Pradesh' : 82232000,
						'Maharashtra' : 122153000,
						'Manipur' : 3103000,
						'Meghalaya' : 3224000,
						'Mizoram' : 1192000,
						'Nagaland' : 2150000,
						'Odisha' : 43671000,
						'Puducherry' : 1504000,
						'Punjab' : 29859000,
						'Rajasthan' : 77264000,
						'Sikkim' : 664000,	
						'Tamil Nadu' : 75695000,
						'Telangana' : 37220000,
						'Tripura' : 3992000,
						'Uttar Pradesh' : 224979000,
						'Uttarakhand' : 11141000,
						'West Bengal' : 96906000
						}
	return population_dict

if __name__ == '__main__': 
	get_state_code_list(data_set)

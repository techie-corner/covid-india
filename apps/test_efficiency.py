#utility functions for test efficiency component

import pandas as pd

from datetime import date 
from datetime import datetime
from datetime import timedelta

data_set = []

def get_tpm_cpm_data(data_set):
    statewise_tested_numbers_data = data_set['statewise_tested_numbers_data']
    statewise_tested_numbers_data.drop(statewise_tested_numbers_data[statewise_tested_numbers_data['Updated On'] == date.today().strftime('%d/%m/%Y')].index, inplace = True)
    statewise_tested_numbers_data.replace('Dadra and Nagar Haveli and Daman and Diu', 'DNHDD',inplace=True) 
    group_data = statewise_tested_numbers_data.groupby('State')
    population_dict = get_state_population(group_data,data_set)
    return group_data, population_dict

def get_state_population(group_data,data_set):
	statewise_tested_numbers_data = data_set['statewise_tested_numbers_data']
	population_dict = {}
	for i in group_data.groups.keys():
		population_dict[i] = statewise_tested_numbers_data[statewise_tested_numbers_data['State']==i]['Population NCP 2019 Projection'].values[0]
	return population_dict

def get_tpm_cpm_table(group_data, population_dict, data_set):
    state_wise_data = data_set['state_wise_data']
    data = state_wise_data.drop(state_wise_data[state_wise_data['State_code'].isin(['TT','UN'])==True].index)
    confirmed_data = state_wise_data.sort_values(by=['State'],ascending=False)
    table_data = {'State': {},
                  'Tests Per Million':{},
                  'Cases Per Million':{}
           }
    data_table = pd.DataFrame(table_data) 
    for i in group_data.groups.keys():
        row = [i,round(group_data.get_group(i)['Total Tested']/(population_dict[i]/1000000)).tail(1).values[0],
          round(confirmed_data[confirmed_data['State'] == i]['Confirmed'].values[0]/(population_dict[i]/1000000))]
        data_table.loc[len(data_table)] = row
    return data_table

if __name__ == '__main__': 
	get_tpm_cpm_data(data_set)
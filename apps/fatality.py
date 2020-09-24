#utility functions for fatality graph component

import pandas as pd
import numpy as np

from datetime import date 
from datetime import datetime
from datetime import timedelta

from apps import death_rate

data_set = []

def get_test_per_positive_data(data_set):
    state_wise_daily_data = data_set['state_wise_daily_data']
    statewise_tested_numbers_data = data_set['statewise_tested_numbers_data']
    last_updated_date = state_wise_daily_data.tail(1)['Date']
    date_time_obj = datetime. strptime(last_updated_date.values[0], '%d-%b-%y')
    last_updated_date = (date_time_obj + timedelta(days = 1)).strftime('%d-%b-%y')
    statewise_tested_numbers_data.drop(statewise_tested_numbers_data[statewise_tested_numbers_data['Updated On'] == date.today().strftime('%d/%m/%Y')].index, inplace = True)
    statewise_tested_numbers_data['Test Positivity'] = round((statewise_tested_numbers_data['Total Tested']/statewise_tested_numbers_data['Positive']))
    test_per_positive_data = statewise_tested_numbers_data.groupby('State')
    return test_per_positive_data

def get_fatality_state_wise_data(data_set,state_code_list):
    state_wise_data = data_set['state_wise_data']
    data = state_wise_data.drop(state_wise_data[state_wise_data['State_code'].isin(['TT','UN'])==True].index)
    confirmed_data = state_wise_data.sort_values(by=['State'],ascending=False).fillna(0)

    table_data = {
        'State':{},
        'Fatality Rate':{},
        'Test Per Positive Case':{}
    }
    data_table = pd.DataFrame(table_data)
    data = death_rate.get_death_confirmed_data(data_set)
    cum_deceased_data = data['state_wise_deceased_data'].cumsum()
    cum_confirmed_data = data['state_wise_confirmed_data'].cumsum()
    test_per_positive_data = get_test_per_positive_data(data_set)
    previous_day = (date.today()  - timedelta(days = 1)).strftime('%d/%m/%Y')
    for i in test_per_positive_data.groups.keys():
        test_per_confirmed = test_per_positive_data.get_group(i).tail(30)
        if i == 'Dadra and Nager Haveli and Daman and Diu':
            i = 'DN & DU'
        state_code = state_code_list[state_code_list['State']==i]['State_code'].values[0]
        fatality_rate = ((cum_deceased_data[state_code]/cum_confirmed_data[state_code])*100).tail(30)
        #table population
        #test_per_confirmed_latest = test_per_confirmed[test_per_confirmed['Updated On']==previous_day]['Test Positivity']
        if confirmed_data[confirmed_data['State'] == i]['Confirmed'].values[0] == 0 or np.isnan(test_per_positive_data.get_group(i)['Total Tested'].tail(1).values[0]):
            test_per_confirmed_latest = None
        else:
            test_per_confirmed_latest = round(test_per_positive_data.get_group(i)['Total Tested'].tail(1).values[0]/confirmed_data[confirmed_data['State'] == i]['Confirmed'].values[0])
        fatality_rate_latest = round(fatality_rate.tail(1).values[0],2)
        row = [i,fatality_rate_latest,test_per_confirmed_latest]
        data_table.loc[len(data_table)] = row
        data_table.sort_values(by=['Fatality Rate'],ascending=False,inplace=True)
    return data_table

if __name__ == '__main__': 
	get_test_per_positive_data(data_set)
	get_fatality_state_wise_data(data_set)
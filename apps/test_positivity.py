#utility methods for test positivity component
import pandas as pd

from datetime import date 
from datetime import datetime

from apps import utility

data_set = []
def get_tests_vs_positive_data(data_set):
    case_time_series_data = data_set['case_time_series_data']
    daily_test_data = data_set['tested_numbers_icmr_data']
    sample_daily_test_data = daily_test_data.tail(14)
    sample_case_data = case_time_series_data.tail(14)
    positivity_rate = []
    no_of_tests = []
    counter = 0
    null_values = ['Nan', 'NaN', 'nan']
    for index, row in sample_case_data.iterrows():
        no_of_tests.append(sample_daily_test_data.values[counter][8])
        if sample_daily_test_data.values[counter][8] not in null_values:
            positivity_rate.append(round((sample_case_data.values[counter][1]/int(sample_daily_test_data.values[counter][8])*100),2))
        counter += 1
    graph_data = {'Date': sample_case_data['Date'],
        'Number Of Tests': no_of_tests,
        'Positive': sample_case_data['Daily Confirmed'],
        'Positivity Rate': positivity_rate
        }

    df = pd.DataFrame (graph_data, columns = ['Date','Number Of Tests','Positive','Positivity Rate'])
    current_date = sample_case_data.tail(1).Date
    return df,current_date,positivity_rate[-1]

def get_state_positivity_data(data_set, state):
    statewise_tested_numbers_data = data_set['statewise_tested_numbers_data']
    statewise_tested_numbers_data.drop(statewise_tested_numbers_data[statewise_tested_numbers_data['Updated On'] == date.today().strftime('%d/%m/%Y')].index, inplace = True)
    group_data = statewise_tested_numbers_data.groupby('State')
    state_data = group_data.get_group(state)
    tests_data = state_data['Total Tested'].diff().tail(14).reset_index(drop=True)

    state_code = utility.get_state_code(data_set, state)

    state_wise_daily_data = data_set['state_wise_daily_data']
    state_wise_confirmed_data = state_wise_daily_data[state_wise_daily_data['Status'] == 'Confirmed']
    state_wise_confirmed_data = state_wise_confirmed_data[['Date',state_code]].tail(14).reset_index(drop=True)

    positivity_rate = round((state_wise_confirmed_data[state_code]/tests_data)*100,2)

    table = {
        "Date": state_wise_confirmed_data['Date'],
        "Number Of Tests": tests_data,
        "Positive": state_wise_confirmed_data[state_code],
        "Positivity Rate": positivity_rate
    }

    df = pd.DataFrame(table)

    current_date = df.tail(1)['Date']
    current_positivity_rate = df.tail(1)['Positivity Rate']
    return df,current_date,current_positivity_rate

if __name__ == '__main__': 
	get_tests_vs_positive_data(data_set)
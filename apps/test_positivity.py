#utility methods for test positivity component
import pandas as pd

data_set = []
def get_tests_vs_positive_data(data_set):
    case_time_series_data = data_set['case_time_series_data']
    daily_test_data = data_set['tested_numbers_icmr_data']
    sample_daily_test_data = daily_test_data.tail(14)
    sample_case_data = case_time_series_data.tail(14)
    positivity_rate = []
    no_of_tests = []
    counter = 0
    for index, row in sample_case_data.iterrows():
        no_of_tests.append(sample_daily_test_data.values[counter][6])
        if sample_daily_test_data.values[counter][6] is not 'Nan' :
            positivity_rate.append(round((sample_case_data.values[counter][1]/int(sample_daily_test_data.values[counter][6])*100),2))
        counter += 1
    graph_data = {'Date': sample_case_data['Date'],
        'Number Of Tests': no_of_tests,
        'Positive': sample_case_data['Daily Confirmed'],
        'Positivity Rate': positivity_rate
        }

    df = pd.DataFrame (graph_data, columns = ['Date','Number Of Tests','Positive','Positivity Rate'])
    return df

if __name__ == '__main__': 
	get_tests_vs_positive_data(data_set)
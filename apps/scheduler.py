import pandas as pd


target_url = 'https://api.covid19india.org/csv/latest/case_time_series.csv'
case_file = pd.read_csv (target_url)
test_file_location = "https://api.covid19india.org/csv/latest/statewise_tested_numbers_data.csv"
test_data = pd.read_csv(test_file_location)
state_wise_daily_url = 'https://api.covid19india.org/csv/latest/state_wise_daily.csv'
state_wise_daily_data = pd.read_csv (state_wise_daily_url)
state_wise_url = 'https://api.covid19india.org/csv/latest/state_wise.csv'
state_wise_data = pd.read_csv(state_wise_url)
daily_test_url = 'https://api.covid19india.org/csv/latest/tested_numbers_icmr_data.csv'
daily_test_data = pd.read_csv (daily_test_url)

#a method to get the csv data on a scheduled-time basis 
def get_data():

	target_url = 'https://api.covid19india.org/csv/latest/case_time_series.csv'
	case_time_series_data = pd.read_csv (target_url)

	test_file_location = "https://api.covid19india.org/csv/latest/statewise_tested_numbers_data.csv"
	statewise_tested_numbers_data = pd.read_csv(test_file_location)

	state_wise_daily_url = 'https://api.covid19india.org/csv/latest/state_wise_daily.csv'
	state_wise_daily_data = pd.read_csv (state_wise_daily_url)

	state_wise_url = 'https://api.covid19india.org/csv/latest/state_wise.csv'
	state_wise_data = pd.read_csv(state_wise_url)

	daily_test_url = 'https://api.covid19india.org/csv/latest/tested_numbers_icmr_data.csv'
	tested_numbers_icmr_data = pd.read_csv (daily_test_url)

	return {"case_time_series_data":case_time_series_data,
	"statewise_tested_numbers_data":statewise_tested_numbers_data,
	"state_wise_daily_data":state_wise_daily_data,
	"state_wise_data":state_wise_data,
	"tested_numbers_icmr_data":tested_numbers_icmr_data
	}

if __name__ == '__main__': 

	get_data()
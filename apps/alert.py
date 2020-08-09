#contains utility functions for getting alert component

data_set = []

#get alert string
def get_death_rate(data_set):
    case_time_series_data = data_set['case_time_series_data']
    total_days = (len(case_time_series_data)*24*60*60)
    total_deaths = case_time_series_data['Daily Deceased'].sum()
    death_rate = total_days/total_deaths
    minutes, sec = divmod(death_rate, 60) 
    hour, minutes = divmod(minutes, 60)
    alert_string = ''
    if hour > 0:
       alert_string += '{} hours '.format(int(hour))
    if minutes > 0:
    	alert_string += '{} minutes '.format(int(minutes))
    if sec > 0:
    	alert_string += '{} seconds'.format(int(sec))
    return alert_string

def get_daily_data(data_set):
    case_time_series_data = data_set['case_time_series_data']
    daily_data = case_time_series_data.tail(1)
    return daily_data[["Daily Confirmed","Daily Recovered","Daily Deceased"]]

if __name__ == '__main__': 

    get_death_rate(data_set)
    get_daily_data(data_set)

#!/usr/bin/python
import pandas as pd
import urllib as ul
import os

####
# This is a script for reading the hourly weather data of the central park weather station from 2013/7/1 - 2013/12/31 from www.wunderground.com.
# The data is stored in a pandas dataframe and saved in a csv file.
# We decide to keep the data for time, temperature, humidity,visibility, wind speed, precipitation, conditions
####

### Get the data from the website and save it as csv
def download_data():

    ### Make folder for saving the data
    cmd = "mkdir WEATHERDATA"
    os.system(cmd)

    ### Define number of days for month
    days_per_month = {7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

    ### Parse the website and read the csv data
    for i in range(7,len(days_per_month)+7):
        for j in range(1,days_per_month[i]+1):

            ### Prepare http string
            date_string = "{0}/{1}".format(i,j)
            http1 = "http://www.wunderground.com/history/airport/KNYC/2013/"
            http2 = "/DailyHistory.html?req_city=New+York&req_state=NY&req_statename=New+York&reqdb.zip=10001&reqdb.magic=1&reqdb.wmo=99999&MR=1&format=1"
            httpin = http1 + date_string + http2

            ### Read the data with pandas
            df = pd.read_csv(ul.urlopen(httpin))

            ### Prepare output file and write with pandas (could be done without pandas as well...)
            date_string2 = "{0}_{1}".format(i,j)
            outfile = "WEATHERDATA/weather_data_2013_" + date_string2 + ".csv"
            df.to_csv(outfile)

            ### Be verbose
            print "Successfully read the data for 2013/" + date_string


### Read the data, from harddrive, into nice pandas frames
def data_to_pandas():

    ### Define number of days for month and get total days
    days_per_month = {7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    days = 0
    for i in range(7,len(days_per_month)+7):
        days += days_per_month[i]

    ### Generate all dates
    dates = pd.date_range('20130701', periods=days, freq = 'D')

    ### Load all data frames in list
    dataframes = []
    for i in range(7,len(days_per_month)+7):
        for j in range(1,days_per_month[i]+1):
            date_string2 = "{0}_{1}".format(i,j)
            dataframes.append(pd.read_csv("WEATHERDATA/weather_data_2013_" + date_string2 + ".csv", delimiter=","))

    ### Prepare final dataset and return
    weatherdata = pd.concat(dataframes, keys = dates)
    return weatherdata


### Drop some columns
def drop_columns(dataset):
    drop_cols = ['Dew PointF', 'Events', 'Gust SpeedMPH', 'Sea Level PressureIn','Wind Direction','WindDirDegrees','DateUTC<br />','Unnamed: 0']
    for i in range(len(drop_cols)):
        dataset.drop(drop_cols[i], axis=1, inplace=True)


### Normalize times
def norm_times(dataset):
    pass
    ### TO DO



########################
#### MAIN FUNCTION ####
########################
if __name__ == "__main__":

    ### Get data (only necessary if not yet downloaded)
    #download_data()

    ### Read into pandas frames
    weather = data_to_pandas()

    ### Drop some irrelevant data
    drop_columns(weather)

    ### Normalize times
    norm_times(weather)

    #print weather.loc['20130701']
    #print weather.loc['20131231']

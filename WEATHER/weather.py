#!/usr/bin/python
__author__ = "karstenk"

### Imports
import pandas as pd
import urllib as ul
import os
import re
import numpy as np
import matplotlib.pyplot as plt


#### This is a script for reading the hourly weather data of the central park weather station from 2013/7/1 - 2013/12/31 from www.wunderground.com
#### The raw data is saved in csv files as well as cleaned and stored in a pandas dataframe



### Get the data from the website and save it as csv
def download_data(foldername):

    ### Make folder for saving the data
    cmd = "mkdir {}".format(foldername)
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
            outfile = foldername + "/weather_data_2013_" + date_string2 + ".csv"
            df.to_csv(outfile)

            ### Be verbose
            print "Successfully read the data for 2013/" + date_string

    ### Get the last day of June as well
    httpinextra = "http://www.wunderground.com/history/airport/KNYC/2013/6/30/DailyHistory.html?req_city=New+York&req_state=NY&req_statename=New+York&reqdb.zip=10001&reqdb.magic=1&reqdb.wmo=99999&MR=1&format=1"
    df = pd.read_csv(ul.urlopen(httpinextra))
    outfileextra = foldername + "/weather_data_2013_6_30.csv"
    df.to_csv(outfileextra)
    print "Successfully read the data for 2013/6/30"



### Read the data from harddrive, clean and process it, and write into nice pandas frames
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

    ### Day counter to check for time change after 125 days
    daycount = 0

    ### Loop over all dataframes
    for i in range(7,len(days_per_month)+7):
        for j in range(1,days_per_month[i]+1):
            date_string2 = "{0}_{1}".format(i,j)
            dataframe = pd.read_csv("WEATHERDATARAW/weather_data_2013_" + date_string2 + ".csv", delimiter=",")

            ### Increment day counter
            daycount += 1

            ### List to store hours with multiple weather measurements
            hours = []

            ### Loop by shape of frame over all rows, do it backwards
            length = dataframe.shape[0]
            for k in range(length):

                ### Before time change? Use EDT time
                if daycount < 126:

                    ### Check EDT time and use first two chars of string as well as am/pm part
                    ### Also note that string lengths differ (10,11,12 are on char longer...). Therefore, look at different positions for am/pm
                    if bool(re.search(':', dataframe['TimeEDT'][length-k-1][0:2])):
                        hour = dataframe['TimeEDT'][length-k-1][0:2] + dataframe['TimeEDT'][length-k-1][5:7]
                    else:
                        hour = dataframe['TimeEDT'][length-k-1][0:2] + dataframe['TimeEDT'][length-k-1][6:8]

                    ### Use always last given time within a started hour to represent this hour, delete everything else
                    ### We do this because we will then shift the data such that each hour is represented by the last value of the preceding one
                    ### Pandas accesses in index[] routine by real row position in frame. But rows were deleted before accessing - therefore we correct for this
                    if hour in hours:
                        dataframe.drop(dataframe.index[[length-k-1]], inplace = True)
                    else:
                        hours.append(hour)

                ### After time change? Use EST time
                else:

                    ### Check EST time and use first two chars of string as well as am/pm part
                    ### Also note that string lengths differ (10,11,12 are on char longer...). Therefore, look at different positions for am/pm
                    #if bool(re.search(':', dataframe['TimeEST'][k][0:2])):
                    if bool(re.search(':', dataframe['TimeEST'][length-k-1][0:2])):
                        hour = dataframe['TimeEST'][length-k-1][0:2] + dataframe['TimeEST'][length-k-1][5:7]
                    else:
                        hour = dataframe['TimeEST'][length-k-1][0:2] + dataframe['TimeEST'][length-k-1][6:8]

                    ### Use always first given time within a started hour to represent this hour, delete everything else
                    ### We do this because we will then shift the data such that each hour is represented by the last value of the preceding one
                    ### Pandas accesses in index[] routine by real row position in frame. But rows were deleted before accessing - therefore we correct for this
                    if hour in hours:
                        dataframe.drop(dataframe.index[[length-k-1]], inplace = True)
                    else:
                        hours.append(hour)

            ### Append to list
            dataframes.append(dataframe)

    ### Check for length of data frames and print if not 24
    ### (one may want to comment this part, as this is only for the identification of the incomplete frames but has no further functionality)
    '''incompletes = 0
    for i in range(len(dataframes)):
        if dataframes[i].shape[0] != 24:
            print "Rows in frame", i+1, ":", dataframes[i].shape[0]
            #print dataframes[i]
            incompletes +=1
    print "There are", incompletes, "frames with incomplete data."'''

    ### Correct these frames by hand (what I do below could also be done with head and tail in a similar fashion)
    ### We always use the time from the next possible measurement, because we obtained value will later be projected onto the following hour
    ### Therefore, this is closer and we get the smaller error
    ### FRAME45: 7:51pm measurement is missing. Copy row from 8:51pm measurement
    dataframes[45] = pd.concat([dataframes[45][:20], dataframes[45][19:]])
    ### FRAME46: 4:51am measurement is missing. Copy row from 5:51am measurement
    dataframes[46] = pd.concat([dataframes[46][:5],dataframes[46][4:]])
    ### FRAME54: 5:51am measurement is missing. Copy row from 6:51am measurement
    dataframes[54] = pd.concat([dataframes[54][:6], dataframes[54][5:]])
    ### FRAME55: 4:51am measurement is missing. Copy row from 5:51am measurement
    dataframes[55] = pd.concat([dataframes[55][:5], dataframes[55][4:]])
    ### FRAME56: 2:51am measurement is missing. Copy row from 3:51am measurement
    dataframes[56] = pd.concat([dataframes[56][:3], dataframes[56][2:]])
    ### FRAME57: 2:51am measurement is missing. Copy row from 3:51am measurement
    ### 6:51pm measurement is also missing. Copy row from 7:51pm measurement
    dataframes[57] = pd.concat([dataframes[57][:3], dataframes[57][2:]])
    dataframes[57] = pd.concat([dataframes[57][:19], dataframes[57][18:]])
    ### FRAME59: 11:51 am measurement is missing. Copy row from 12:51pm measurement
    dataframes[59] = pd.concat([dataframes[59][:12], dataframes[59][11:]])
    ### FRAME64: 9:51pm measurement is missing. Copy row from 10:51pm measurement
    dataframes[64] = pd.concat([dataframes[64][:22], dataframes[64][21:]])
    ### FRAME66: 9:51am measurement is missing. Copy row from 10:51am measurement
    dataframes[66] = pd.concat([dataframes[66][:10], dataframes[66][9:]])
    ### FRAME125: 11:51pm measurement is missing. Copy row from 12:51am measurement from next dataframe
    dataframes[125] = pd.concat([dataframes[125][:23], dataframes[126][:1]])
    ### FRAME168: 4:51am measurement is missing. Copy row from 5:51am measurement
    dataframes[168] = pd.concat([dataframes[168][:5], dataframes[168][4:]])

    ### Check again for length of data frames and print if not 24
    ### (one may want to comment this part, as this is only for the identification of the incomplete frames but has no further functionality)
    '''incompletes = 0
    for i in range(len(dataframes)):
        if dataframes[i].shape[0] != 24:
            print "Rows in frame", i+1, ":", dataframes[i].shape[0]
            #print dataframes[i]
            incompletes +=1
    print "There are", incompletes, "frames with incomplete data."'''

    ### Most measurements are taken at around xx:51. Therefore, it makes more sense to project them onto the following hour than on the preceding
    ### This requires, however, to resort all data as the first 12:00am measurement of a given frame is then the 11:51pm measurement of the preceding frame
    ### Go backwards through the list and resort times
    for i in range(len(dataframes)):
        if i == len(dataframes)-1:
            dataframes[len(dataframes)-i-1] = pd.concat([pd.read_csv("WEATHERDATARAW/weather_data_2013_6_30.csv", delimiter=",").tail(n=1), dataframes[len(dataframes)-i-1].head(n=23)])
        else:
            dataframes[len(dataframes)-i-1] = pd.concat([dataframes[len(dataframes)-i-2].tail(n=1), dataframes[len(dataframes)-i-1].head(n=23)])

    ### Now we have proper frames with 24 measurements for each day, concatenate them
    weatherdata = pd.concat(dataframes)

    ### Clean the messed up index
    weatherdata = weatherdata.reset_index(drop=True)

    ### Done, return
    return weatherdata



### Reindex the dataframes with proper time object as well as reduced time data
def time_index(dataset):

    ### Make a time series and set on dataset
    timeindex = pd.date_range('20130701', periods=24*184, freq='H')
    dataset["Time"] =pd.Series(timeindex, index=dataset.index)

    ### Set month, starting from 7 (default)
    dataset["Month"] = pd.Series(timeindex.month, index=dataset.index)

    ### Set day of month, starting from 1 (default)
    dataset["DayOfMonth"] = pd.Series(timeindex.day, index=dataset.index)

    ### Set day of week, starting from 0 (default)
    dataset["DayOfWeek"] = pd.Series(timeindex.weekday, index=dataset.index)

    ### Set day of week, starting from 0 (default)
    dataset["Hour"] = pd.Series(timeindex.hour, index=dataset.index)

    ### Set absolute row/measurement number as well as day number, both starting from 0
    numbers = []
    days = []
    for i in range(184*24):
        numbers.append(i)
        days.append(i/24)
    dataset["Number"] = pd.Series(numbers, index=dataset.index)
    dataset["AbsoluteDay"] = pd.Series(days, index=dataset.index)



### Arrange and drop some columns
def arrange_columns(dataset):

    ### Drop some columns which will be most probably not used
    drop_cols = ['Dew PointF', 'Events', 'Gust SpeedMPH','Wind Direction','WindDirDegrees','DateUTC<br />','Unnamed: 0','TimeEST','TimeEDT']
    for i in range(len(drop_cols)):
        dataset.drop(drop_cols[i], axis=1, inplace=True)

    ### Rearrange columns
    dataset = dataset[["Number", "Time", "AbsoluteDay", "Month", "DayOfMonth", "DayOfWeek", "Hour", "TemperatureF", "PrecipitationIn", "Humidity", "Sea Level PressureIn", "VisibilityMPH", "Conditions", "Wind SpeedMPH"]]

    ### Rename columns, no spaces
    dataset.rename(columns={"Sea Level PressureIn": "SeaLevelPressureIn", "Wind SpeedMPH": "WindSpeedMPH"}, inplace=True)

    ### Done, return
    return dataset



### Clean the temperature, windspeed and pressure data, which has -9999.0, when data is missing
def clean_corrupt_data(dataset):

    ### -9999.0 appears in the data, when there is an individual measurement missing
    ### Change these to NaN's, which are usually used for this in pandas. Start with temperature, pressure and visibility
    for i in list(dataset[dataset["TemperatureF"] == -9999.0].index.values):
        dataset.at[i, "TemperatureF"] = np.nan
    for i in list(dataset[dataset["VisibilityMPH"] == -9999.0].index.values):
        dataset.at[i, "VisibilityMPH"] = np.nan
    for i in list(dataset[dataset["SeaLevelPressureIn"] == -9999.0].index.values):
        dataset.at[i, "SeaLevelPressureIn"] = np.nan

    ### Now the Wind Speed data. First, "Calm" can be safely approximated by 0.0.
    for i in list(dataset[dataset["WindSpeedMPH"] == "Calm"].index.values):
        dataset.at[i, "WindSpeedMPH"] = "0.0"

    ### For the -9999.0 issue, we have to preceed differently as before because we don't deal with floats here
    ### Somehow it only works when changing first to string type, then perform change, then change to float
    dataset[['WindSpeedMPH'] ] = dataset[['WindSpeedMPH']].astype(str)
    for i in list(dataset[dataset["WindSpeedMPH"] == "-9999.0"].index.values):
        dataset.at[i, "WindSpeedMPH"] = "NaN"
    dataset[['WindSpeedMPH'] ] = dataset[['WindSpeedMPH']].astype(float)



### write dataset to csv file with provided filename
def write_to_csv(dataset, filename):

    dataset.to_csv(filename)



### pickle dataset with provided filename
def write_pickle(dataset, filename):

    dataset.to_pickle(filename)



### Class holding evaluations and visualizations (implement more if necessary)
class Evaluations(object):

    def __init__(self, data):
        self._data = data

    ### Print properties
    def properties(self):
        print "DESCRIBE:"
        print self._data.describe(), "\n"
        print "DTYPES:"
        print self._data.dtypes, "\n"

    ### Draw numerical data as cruves
    def curve(self, first, *rest):
        self._data[first].plot()
        for string in list(rest):
            self._data[string].plot()
        plt.show()

    ### Print numbers of uniques in non-numerical data
    def uniques(self, first, *rest):
        print "Column:", first
        print self._data[first].value_counts(), "\n"
        for string in list(rest):
            print "Column:", string
            print self._data[string].value_counts(), "\n"




########################
#### MAIN FUNCTION ####
########################
if __name__ == "__main__":

    ### Get data, only necessary if not yet downloaded
    if not os.path.isdir("WEATHERDATARAW"):
        download_data("WEATHERDATARAW")

    ### Read into pandas frames
    weather = data_to_pandas()

    ### Make proper time indices
    time_index(weather)

    ### Drop some irrelevant data and arrange columns
    weather = arrange_columns(weather)

    ### Clean some corrupt data
    clean_corrupt_data(weather)

    ### Write final clean dataset to csv, only necessary if not yet done
    if not os.path.isfile("clean_weather.csv"):
        write_to_csv(weather, "clean_weather.csv")

    ### Write final clean dataset to csv, only necessary if not yet done
    if not os.path.isfile("clean_weather.pkl"):
        write_pickle(weather, "clean_weather.pkl")


    ### Have a quick look at the data to make sure everything looks reasonable
    ### This could be deleted as it has no further functionality
    SomeEvals = Evaluations(weather)
    ### Check basic properties
    SomeEvals.properties()
    ### Check the non numerical data
    SomeEvals.uniques("Conditions")
    ### Check temperature, draw curve
    SomeEvals.curve("TemperatureF")
    SomeEvals.curve("PrecipitationIn")

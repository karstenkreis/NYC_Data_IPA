__author__ = 'eladg'
import csv
import os
import datetime

fileOut = open('allTaxiData.csv', 'w')
writer = csv.writer(fileOut, delimiter=',')

filePath = './NYC Taxi Data/NYC Yellow Taxi Data/2014/Trips/'
fileList = os.listdir(filePath)
fileList = [fileList[i] for i in [9, 10, 11, 1, 2, 3]]  # Only use July-Dec files
chosenEntries = range(7, 14)
fileInd = 0
for name in fileList:
    fileIn = open(filePath + '/' + name, 'r')
    reader = csv.reader(fileIn, delimiter=',')

    lineInd = 0
    for line in reader:
        lineInd += 1
        vals = [line[i] for i in chosenEntries]
        if lineInd == 1:
            if fileInd > 1:  # don't include header except once in the beginning
                continue
            vals = [x.strip() for x in vals]
            header = ['Day of year', 'Day of Month', 'Day of week', 'Month', 'Hour'] + vals
            writer.writerow(header)
            continue

        pickupDate = datetime.datetime.strptime(line[5], '%Y-%m-%d %H:%M:%S')
        dropoffDate = datetime.datetime.strptime(line[6], '%Y-%m-%d %H:%M:%S')

        dayOfYear = pickupDate.timetuple().tm_yday
        dayOfWeek = pickupDate.weekday()
        dayOfMonth = pickupDate.day
        month = pickupDate.month
        hour = pickupDate.hour

        if month < 7:
            continue

        if pickupDate.minute > 30:
            hour += 1

        outLine = [dayOfYear, dayOfMonth, dayOfWeek, month, hour] + vals

        writer.writerow(outLine)
        # nOut = (len(line) - 3)/entriesPerLine
        # for outInd in xrange(0,nOut):
        #     outLine = prefix + line[outInd*entriesPerLine + 3 : (outInd+1)*entriesPerLine + 3]
        #     writer.writerow(outLine)

    fileIn.close()

fileOut.close()

# Note: Deprecated as link is out of date

import requests
import re
from bs4 import BeautifulSoup
import sqlite3
import threading
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
import time

website_url = requests.get('https://www.esrl.noaa.gov/gmd/aggi/aggi.html').text
yearRegex = re.compile("<td>(\d\d\d\d)<\/td>")
dataRegex = re.compile("<td>(\d\.\d\d\d)<\/td>")
soup = BeautifulSoup(website_url,'lxml')
dataTable = soup.find('table',{'class':'table table-bordered table-condensed table-striped table-header'})

data = dataTable.find_all('td')
yearList = []
templist = []
for i in data:
    years = yearRegex.findall(str(i))
    if years:
        yearList.append(years)
    dataTest = dataRegex.findall(str(i))
    if dataTest:
        templist.append(dataTest)

for i in range(len(templist)):
    templist[i] = templist[i][0]
for i in range(len(yearList)):
    yearList[i] = int(yearList[i][0])

co2List = []
ch4List = []
n2oList = []
cfc12List = []
cfc11List = []
minor15List = []

appendDict = {0:co2List, 1:ch4List, 2:n2oList, 3:cfc12List, 4:cfc11List, 5:minor15List}

for i in range(8, len(templist) + 1, 8):
  tempData = templist[i-8:i-2]
  for i in range(len(tempData)):
      appendDict[i].append(float(tempData[i]))

def createSQLiteTable(): # Creates database
    try:
        sqliteConnection = sqlite3.connect('lab3database.db')
        sqlite_create_table_query = '''CREATE TABLE Database (
                                    year int NOT NULL,
                                    co2 float NOT NULL,
                                    ch4 float NOT NULL,
                                    n2o float NOT NULL,
                                    cfc12 float NOT NULL,
                                    cfc11 float NOT NULL,
                                    minor15 float NOT NULL);'''
        cursor = sqliteConnection.cursor()
        print("Successfully Connected to SQLite")
        cursor.execute(sqlite_create_table_query)
        sqliteConnection.commit()
        print("SQLite table created")
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table", error)

def insertData(insertionData): # Inserts data
    try:
        sqliteConnection = sqlite3.connect('lab3database.db')
        cursor = sqliteConnection.cursor()
        sqlite_insert_blob_query = """ INSERT INTO Database
                                  (year, co2, ch4, n2o, cfc12, cfc11, minor15) VALUES (?, ?, ?, ?, ?, ?, ?)"""
        data_tuple = (insertionData)
        cursor.execute(sqlite_insert_blob_query, data_tuple)
        sqliteConnection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table", error)

def insertTableData():
    for i in range(len(yearList)):
        tempTuple = (yearList[i], co2List[i], ch4List[i], n2oList[i], cfc12List[i], cfc11List[i], minor15List[i])
        insertData(tempTuple)

# createSQLiteTable()
# insertTableData()

def readSqliteTable(threadID, threadList):
    try:
        sqliteConnection = sqlite3.connect('lab3database.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sqlite_select_query = """SELECT * from Database"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        for row in records:
            threadList.append(row[threadID + 1])
        cursor.close()
        # return returnYearList, returnDataList
        return threadList
    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)


class dataThread(threading.Thread):
    def __init__(self, dataList, threadID, dataText):
        threading.Thread.__init__(self)
        self.dataList = dataList
        self.threadID = threadID
        self.dataText = dataText

    def getData(self):
        threadLock.acquire()
        self.dataList = readSqliteTable(self.threadID, self.dataList)
        threadLock.release()

    def printData(self):
        print(self.dataList)

    def LinRegression(self):
        """
        Calculates the linear regression, then saves an image to the file
        :return:
        """
        self.yearList = np.array(yearList)
        self.dataList = np.array(self.dataList)
        self.yearList = np.reshape(self.yearList,(-1, 1))
        self.dataList = np.reshape(self.dataList,(-1, 1))
        linear_regressor = LinearRegression()  # create object for the class
        linear_regressor.fit(self.yearList, self.dataList)  # perform linear regression
        Y_pred = linear_regressor.predict(self.yearList)  # make predictions
        plt.scatter(self.yearList, self.dataList)
        plt.plot(self.yearList, Y_pred, color='red')
        plt.title("Linear Regression")
        plt.xlabel(self.dataText)
        plt.ylabel(self.dataText)
        plt.show()
        plt.cla()

    def run(self):
        self.getData()
        self.printData()
        self.LinRegression()
        print("this is thread", self.threadID)




threadList = []
threadLock = threading.Lock()
co2DataList = []
ch4DataList = []
n2oDataList = []
cfc12DataList = []
cfc11DataList = []
minor15DataList = []
threadDataList = {0:co2DataList, 1: ch4DataList, 2:n2oDataList, 3:cfc12DataList, 4:cfc11DataList, 5:minor15DataList}
threadDataText = {0:"CO2", 1:"CH4", 2:"N2O", 3:"CFC12", 4:"CFC11", 5:"Minor15"}

for i in range(6):
    threadList.append(dataThread(threadDataList[i], i, threadDataText[i]))
    threadList[-1].start()
    time.sleep(0.2)

for i in threadList:
     i.join()

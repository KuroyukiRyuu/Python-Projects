import pandas
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

df = pandas.read_csv("AGGI_Table.csv")


for i in range(1, 7):
    yearList = df.iloc[:, 0].to_numpy()
    dataList = df.iloc[:, i].to_numpy()

    yearList = yearList.reshape(1, -1)
    dataList = dataList.reshape(1, -1)

    linear_regressor = LinearRegression()
    linear_regressor.fit(yearList, dataList)
    Y_pred = linear_regressor.predict(yearList)
    plt.scatter(yearList, dataList)
    plt.plot(yearList.tolist(), Y_pred, color='green')

    plt.title(df.columns[i] + " per year")
    plt.xlabel("Year")
    plt.ylabel(df.columns[i])
    plt.show()
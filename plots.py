import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime

hourDF = pd.read_csv('data/2017_hourly.csv')
n_season = 4 # as the labels go in dataset: 1 = winter, 2 = spring, 3 = summer, 4 = fall
n_weather = 4
n_hours = 24
n_temp_interval = 8
dtemp = 1.0 / n_temp_interval

temp_interval = []
for i in hourDF.index:
    k = int(hourDF.temp[i] * n_temp_interval)
    if k==n_temp_interval: # there is one data point where temp = 1.0, we bin it to (35.875, 41]
        k -= 1
    temp_interval.append(k)

df1 = pd.DataFrame({'weather': hourDF.condition, 'temp_interval': temp_interval, 'cnt': hourDF.total})
m1 = df1.groupby(['weather', 'temp_interval'])['cnt'].mean().reset_index()

M1 = np.zeros((n_weather, n_temp_interval))
for i in m1.index:
    weather = m1.weather[i]-1
    temp_int = m1.temp_interval[i]
    M1[weather][temp_int] = m1.cnt[i]

# usage by weather and temperature condition
fig1 = plt.gca()
xticklabels = [i*dtemp for i in range(0, n_temp_interval)]
yticklabels = ['clear', 'cloudy', 'light', 'severe']

sns.heatmap(data=M1, annot=True, fmt = ".1f", xticklabels=xticklabels, yticklabels=yticklabels)
plt.title('mean usage count')
plt.xlabel('normalized temperature')
plt.ylabel('weather condition')
plt.show()

df2 = pd.DataFrame({'season': hourDF.season, 'hour': hourDF.hr, 'cnt': hourDF.total})
m2 = df2.groupby(['season', 'hour'])['cnt'].mean().reset_index()
print(m2)

M2 = np.zeros((n_season, n_hours))
for i in m2.index:
    season = m2.season[i]-1
    hour = m2.hour[i]
    M2[season][hour] = m2.cnt[i]

hr_range = [i for i in range(0, n_hours)]
hr_range2 = [2*i for i in range(0, int(n_hours/2))]

# Hourly usage by season - with correct season labels
# mark these in bargraphs
fig2, axes = plt.subplots(2, 2, sharex='col', sharey='row')
sns.regplot('hour', 'cnt', data=m2.iloc[0:n_hours], fit_reg=False, ax = axes[0,0])
axes[0,0].set_title('winter')
axes[0,0].set_xticks(hr_range2)
axes[0,0].set_xlabel('')
axes[0,0].set_ylabel('seasonal usage count')
axes[0,0].set_ylim(0.0, 850.0)
axes[0,0].yaxis.set_label_coords(-0.2,0.0)
sns.regplot('hour', 'cnt', data=m2.iloc[n_hours+1:2*n_hours], fit_reg=False, ax = axes[0,1])
axes[0,1].set_title('spring')
axes[0,1].set_xlabel('')
axes[0,1].set_ylabel('')
sns.regplot('hour', 'cnt', data=m2.iloc[2*n_hours+1:3*n_hours], fit_reg=False, ax = axes[1,0])
axes[1,0].set_title('summer')
axes[1,0].set_xlabel('hour')
axes[1,0].set_ylim(0.0, 850.0)
axes[1,0].xaxis.set_label_coords(1.1,-0.15)
axes[1,0].set_ylabel('')
sns.regplot('hour', 'cnt', data=m2.iloc[3*n_hours+1:4*n_hours], fit_reg=False, ax = axes[1,1])
axes[1,1].set_title('fall')
axes[1,1].set_xticks(hr_range2)
axes[1,1].set_ylabel('')
axes[1,1].set_xlabel('')
plt.show()

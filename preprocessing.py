import json

import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt

# this is the station which has wrong station_id in station_information
# so its capacity info is missing
missing_capacity = {
                    '7029' : 15 # Bay St / Bloor St W
                    }

HourlyDF = pd.read_csv('data/2017_hourly.csv', usecols=['season', 'date'])
SeasonDF = HourlyDF.groupby('date').sum()

for i in SeasonDF.index:
    SeasonDF.loc[i] /= 24

use_cols = ['trip_duration_seconds',
            'trip_start_date',
            'from_station_id',
            'from_station_name',
            'to_station_id',
            'to_station_name',
            'trip_start_time'
           ]

EventsDF = pd.read_csv('data/2017_events_joined.csv', usecols=use_cols)

# keep trips between 1 min to 30 min (91% of whole data set)
EventsDF = EventsDF[EventsDF['trip_duration_seconds'] < 1800]
EventsDF = EventsDF[EventsDF['trip_duration_seconds'] > 60]

# just keep the hour
for i in EventsDF.index:
    EventsDF.at[i, 'trip_start_time'] = int(EventsDF.trip_start_time[i].split(":")[0])

# station names that appear in the trip events table
station_names = set(EventsDF.from_station_name.values)

capacity = {}

with open('data/station_information.json', "r") as f:
    station_info = json.load(f)

for station in station_info['data']['stations']:
    if station['station_id'] in missing_capacity.keys():
        capacity.update({int(station['station_id']) : missing_capacity[station['station_id']]})
    else:
        capacity.update({int(station['station_id']) : station['capacity']})

# compute the average hourly time series using all the data, or breaking into
# subsets consisting of winter + spring, and summer + fall averages
usageTS = pd.DataFrame(np.zeros((len(station_names), 24)), index=station_names, columns=range(0,24))
winter_spring_TS = pd.DataFrame(np.zeros((len(station_names), 24)), index=station_names, columns=range(0,24))
summer_fall_TS = pd.DataFrame(np.zeros((len(station_names), 24)), index=station_names, columns=range(0,24))

for i in EventsDF.index:
    date = EventsDF.at[i, 'trip_start_date']
    season = SeasonDF.loc[date][0]
    from_station_id = EventsDF.at[i, 'from_station_id']
    to_station_id = EventsDF.at[i, 'to_station_id']
    from_station_name = EventsDF.at[i, 'from_station_name']
    to_station_name = EventsDF.at[i, 'to_station_name']
    hr = EventsDF.at[i, 'trip_start_time']

    usageTS.loc[from_station_name][hr] -= 1.0 / capacity[from_station_id]
    usageTS.loc[to_station_name][hr] += 1.0 / capacity[to_station_id]

    if season == 1 or season == 2:
        winter_spring_TS.loc[from_station_name][hr] -= 1.0 / capacity[from_station_id]
        winter_spring_TS.loc[to_station_name][hr] += 1.0 / capacity[to_station_id]
    else:
        summer_fall_TS.loc[from_station_name][hr] -= 1.0 / capacity[from_station_id]
        summer_fall_TS.loc[to_station_name][hr] += 1.0 / capacity[to_station_id]

# average by the number of days for each subset
usageTS /= 365.0
winter_spring_TS /= 181.0
summer_fall_TS /= 184.0

usageTS.to_csv('usage_all.csv')
winter_spring_TS.to_csv('usage_q1q2.csv')
summer_fall_TS.to_csv('usage_q3q4.csv')

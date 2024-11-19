# -*- coding: utf-8 -*-
"""
Created on Mo Jan 8 11:24:02 2023

@author: burgerin

https://stackoverflow.com/questions/23576970/python-handling-username-and-password-for-url
https://docs.python-requests.org/en/latest/
https://docs.streamlit.io/streamlit-community-cloud/get-started/quickstart

"""

## import needed packages
import streamlit as st

import plotly.io as pio
import plotly.express as px

import requests
import pandas as pd
import io

import datetime
import numpy as np

# set start and end date
today = datetime.date.today()
history = today - datetime.timedelta(days=7)
start_date = history
end_date = today - datetime.timedelta(days=1)

## visualize start and end data --> cannot not be editted by the user
# st.write('start date: '+str(start_date))
# st.write('end date: '+str(end_date))

# Download data file (gathered by API call performed by UTwente and stored in csv)
# by making use of the requests python package
# and for the selected date range
url = "http://majisysdemo.itc.utwente.nl/wunder/get7days.py?location=z6-08820"
## download url
urlData = requests.get(url).content
## transform requests format to pandas
rawData = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
## remove header lines (1 and 2, keep 0 since this includes the abbreviation of the parameters)
df = rawData.drop([0]).reset_index(drop=True)

# print(df)

def numeric_mean(df_in,var,re_int):

    df_in[var] = pd.to_numeric(df_in[var], errors='coerce')
    df_out = df_in.resample(re_int)[var].mean()
    
    return df_out

## needed statistics

df['datetime'] = pd.to_datetime(df['Date'])

# Set the datetime column as the index
df.set_index('datetime', inplace=True)

print(df.columns)

## aggregation hourly of selected parameters

## precipitation
df_hourly_P_sum = df.resample('h')['Precipitation observed'].sum()

## windspeed
df_daily_wind_min = df.resample('d')['Wind speed observation'].min()
df_daily_wind_max = df.resample('d')['Wind speed observation'].max()
df_daily_wind_avg = numeric_mean(df,'Wind speed observation','d')
df_hourly_wind_avg = numeric_mean(df,'Wind speed observation','h')

## air temperature
df_daily_Tair_min = df.resample('d')['Air Temperature observation'].min()
df_daily_Tair_max = df.resample('d')['Air Temperature observation'].max()
df_daily_Tair_avg = numeric_mean(df,'Air Temperature observation','d')
df_daily_Tair_avg = numeric_mean(df,'Air Temperature observation','h')

## plot with plotly
pio.renderers.default='browser'
pd.options.plotting.backend = "plotly"
# pio.templates.default = "plotly"
fig = df_hourly_P_sum.plot(x=df_hourly_P_sum.index,y='Precipitation observed')
# fig.update_layout(hovermode="x unified",xaxis_title=None,yaxis_title='windflux [m/s]')
## set date range maximum on end_date + 1
# if end_date==today:
#     fig.update_xaxes(range = [start_date,today])
# else:
#     fig.update_xaxes(range = [start_date,end_date + datetime.timedelta(days=1)])

## create simple dashboard
st.plotly_chart(fig)

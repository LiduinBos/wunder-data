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

def numeric_mean(df_in,var,re_int,method):

    df_in[var] = pd.to_numeric(df_in[var], errors='coerce')

    if method=='mean':
        df_out = df_in.resample(re_int)[var].mean()
    elif method=='sum':
        df_out = df_in.resample(re_int)[var].sum()
    elif method=='min':
        df_out = df_in.resample(re_int)[var].min()
    elif method=='max':
        df_out = df_in.resample(re_int)[var].max()

    return df_out

## needed statistics

df['datetime'] = pd.to_datetime(df['Date'])

# Set the datetime column as the index
df.set_index('datetime', inplace=True)

print(df.columns)

## aggregation hourly of selected parameters

## precipitation
# df_hourly_P_sum = df.resample('h')['Precipitation observed'].sum()
df_hourly_P_sum = numeric_mean(df,'Precipitation observed','h','sum')
df_total_P_sum = df_hourly_P_sum.sum()
df_total_P_avg = df_hourly_P_sum.mean()
df_total_P_max = df_hourly_P_sum.max()

print(df_total_P_sum,df_total_P_avg,df_total_P_max)

## windspeed
df_daily_wind_min = numeric_mean(df,'Wind speed observation','d','min')
df_daily_wind_max =numeric_mean(df,'Wind speed observation','d','max')
df_daily_wind_avg = numeric_mean(df,'Wind speed observation','d','mean')
df_hourly_wind_avg = numeric_mean(df,'Wind speed observation','h','mean')

## air temperature
df_daily_Tair_min = numeric_mean(df,'Air Temperature observation','d','min')
df_daily_Tair_max = numeric_mean(df,'Air Temperature observation','d','max')
df_daily_Tair_avg = numeric_mean(df,'Air Temperature observation','d','mean')
df_hourly_Tair_avg = numeric_mean(df,'Air Temperature observation','h','mean')

## plot with plotly
pio.renderers.default='browser'
pd.options.plotting.backend = "plotly"

# fig = df_hourly_P_sum.plot(x=df_hourly_P_sum.index,y='Precipitation observed')
# Create the bar plot
fig1 = px.bar(
    df_hourly_P_sum,
    x=df_hourly_P_sum.index,
    y='Precipitation observed',
    labels={'x': 'Date', 'Precipitation observed': 'Precipitation [mm]'}
)
fig1.update_layout(hovermode="x unified",
                #   title = 'Precipitation during the last 7 days',
                  xaxis_title='Date',
                  yaxis_title='Precipitation - hourly sum [mm]',
                  margin=dict(r=150), # Add extra margin to make space for the box)
)  

# Update hover template
fig1.data[0].update(
    hovertemplate='%{x}<br>Precipitation: %{y:.2f} mm<extra></extra>'
)

# Add a box with statistics
stats_text = (
    f"<b>Statistics over 7 days</b><br>"
    f"Total sum: {df_total_P_sum:.2f} mm<br>"
    f"Average: {df_total_P_avg:.2f} mm<br>"
    f"Max: {df_total_P_max:.2f} mm"
)

fig1.add_annotation(
    text=stats_text,
    xref="paper", yref="paper",  # Position in terms of the plot (0-1 range)
    x=1.2, y=0.95,  # Top-right corner of the plot
    showarrow=False,  # No arrow
    align="left",
    bgcolor="rgba(255, 255, 255, 0.8)",  # Background color with transparency
    bordercolor="black",
    borderwidth=1
)

# ## create simple dashboard
# st.plotly_chart(fig)

# Second Plot (Plotly Line Plot)
fig2 = px.line(
    df_hourly_Tair_avg,
    x=df_hourly_Tair_avg.index,
    y='Air Temperature observation',
    labels={'x': 'Date', 'Air Temperature observation': 'Temperature [C]'},
)
fig2.update_traces(marker=dict(size=8, symbol='circle'), line=dict(color='blue'))

# Streamlit Layout
st.title("Weather data Herenboeren Wenumseveld for the past 7 days")

# First Plot Section
st.subheader("Precipitation")
st.plotly_chart(fig1)

# Second Plot Section
st.subheader("Temperature")
st.plotly_chart(fig2)

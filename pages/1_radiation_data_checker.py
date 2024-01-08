# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 13:04:18 2023

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

# set start and end date
# make it variables that can be chosen in the app as a given range
today = datetime.date.today()
history = today - datetime.timedelta(days=7)
start_date = st.date_input('Start date', history,min_value=datetime.datetime(2023, 12, 1),max_value=today - datetime.timedelta(days=2))
## set max end_date on today - 1 day since data is only stored till midnight of today
end_date_max = today - datetime.timedelta(days=1)
end_date = st.date_input('End date', end_date_max,min_value=datetime.datetime(2023, 12, 1),max_value=end_date_max)
if start_date < end_date:
    # st.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
    pass
else:
    st.error('Error: End date must fall after start date.')

## set date range for data to be downloaded
daterange = [d.strftime('%Y%m%d') for d in pd.date_range(start_date,end_date + datetime.timedelta(days=1))]

## select parameter set
pars = "cnr4"

## account credentials of ftp server from where data will be downloaded
username = 'liduin'
password = 'WunDer@2024;'

# Download data files
# by making use of the requests python package
# and for the selected date range
i=0
for date in daterange:
    url = "http://liduin:WunDer@2024;@majisysdemo.itc.utwente.nl/wunder/logger_files/Wenumseveld_EC/CR3000_Wenumseveld_"+pars+"_ts"+date+".dat"
    ## download url
    urlData = requests.get(url, auth=(username, password)).content
    ## transform requests format to pandas
    # https://stackoverflow.com/questions/39213597/convert-text-data-from-requests-object-to-dataframe-with-pandas
    rawData = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
    ## remove header lines (1 and 2, keep 0 since this includes the abbreviation of the parameters)
    df = rawData.drop([1,2]).reset_index(drop=True)
    df.columns = df.iloc[0] ##--> header is not fully set yet, is now in row 0
    df2 = df.drop([0]).reset_index(drop=True)
    ## concatenate all data to 1 dateframe
    if i==0:
        df_all = df2
    else:
        df_all = pd.concat([df_all,df2])
    i+=1

## plot with plotly
pio.renderers.default='browser'
pd.options.plotting.backend = "plotly"
# pio.templates.default = "plotly"
fig = df_all.plot(x='TIMESTAMP',y=['Rs_in','Rs_out','Rl_in','Rl_out'])
fig.update_layout(hovermode="x unified",xaxis_title=None,yaxis_title='Radiation [W/m2]')
## set date range maximum on end_date + 1
if end_date==today:
    fig.update_xaxes(range = [start_date,today])
else:
    fig.update_xaxes(range = [start_date,end_date + datetime.timedelta(days=1)])

## create simple dashboard
st.plotly_chart(fig)
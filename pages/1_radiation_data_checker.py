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

# import plotly as pl
import plotly.io as pio
import plotly.express as px

import requests
import pandas as pd
import io

# Download data files
# by making use of the requests python package
pars = "cnr4"
date = "20231201"
url = "http://liduin:WunDer@2024;@majisysdemo.itc.utwente.nl/wunder/logger_files/Wenumseveld_EC/CR3000_Wenumseveld_"+pars+"_ts"+date+".dat"
username = 'liduin'
password = 'WunDer@2024;'
urlData = requests.get(url, auth=(username, password)).content

## transform requests format to pandas
# https://stackoverflow.com/questions/39213597/convert-text-data-from-requests-object-to-dataframe-with-pandas
rawData = pd.read_csv(io.StringIO(urlData.decode('utf-8')))

## remove header lines (1 and 2, keep 0 since this includes the abbreviation of the parameters)
df = rawData.drop([1,2]).reset_index(drop=True)
df.columns = df.iloc[0] ##--> header is not fully set yet, is now in row 0
df2 = df.drop([0]).reset_index(drop=True)

## plot with plotly
pio.renderers.default='browser'
pd.options.plotting.backend = "plotly"
# pio.templates.default = "plotly"
fig = df2.plot(x='TIMESTAMP',y=['Rs_in','Rs_out','Rl_in','Rl_out'])
# fig = px.line(df2,x='TIMESTAMP',y=['Rs_in','Rs_out','Rl_in','Rl_out'])

# fig.show()

## create simple dashboard
st.plotly_chart(fig)
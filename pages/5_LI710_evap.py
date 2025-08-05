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
pars = "LI710group0"

## account credentials of ftp server from where data will be downloaded
username = 'liduin'
password = 'WunDer@2024;'

# Download data files
# by making use of the requests python package
# and for the selected date range
i=0
for date in daterange:
    url = "http://liduin:WunDer@2024;@majisysdemo.itc.utwente.nl/wunder/logger_files/Wenumseveld_EC/CR3000_Wenumseveld_"+pars+date+".dat"
    ## download url
    urlData = requests.get(url, auth=(username, password)).content
    ## transform requests format to pandas
    # https://stackoverflow.com/questions/39213597/convert-text-data-from-requests-object-to-dataframe-with-pandas
    rawData = pd.read_csv(io.StringIO(urlData.decode('utf-8')),skiprows=[0,2,3])
    # ## remove header lines (1 and 2, keep 0 since this includes the abbreviation of the parameters)
    # df = rawData.drop([1,2]).reset_index(drop=True)
    # df.columns = df.iloc[0] ##--> header is not fully set yet, is now in row 0
    # df2 = df.drop([0]).reset_index(drop=True)
    df2 = rawData
    ## concatenate all data to 1 dateframe
    if i==0:
        df_all = df2
    else:
        df_all = pd.concat([df_all,df2])
    i+=1
st.write(df_all.columns)
## determine net radiation
# df_all['SWTop'] = pd.to_numeric(df_all['SWTop_Avg']) 
#df_all['SWBottom'] = pd.to_numeric(df_all['SWBottom_Avg'])
#df_all['LWTop_cor'] = pd.to_numeric(df_all['LWTopC_Avg'])
#df_all['LWBottom_cor'] = pd.to_numeric(df_all['LWBottomC_Avg'])
#df_all['Rn'] =  (df_all['SWTop']-df_all['SWBottom'])+(df_all['LWTop_cor']-df_all['LWBottom_cor'])

df_all['et_l'] = df_all['et_l'].replace('NAN', '')

df_all['et_l'] = pd.to_numeric(df_all['et_l'])*48.0 ## including conversion from mm/30min to mm/day
df_all['et_le_l'] = pd.to_numeric(df_all['le_l'])*0.035 ## simple conversion from le to et including conversion from mm/30min to mm/day

# Define custom labels
custom_labels = {
    "et_l": "evaporation [mm]",
    "le_l": "latent heat [W/m2]",
    "et_le_l": "converted latent heat [mm/day]",
}

#df_plot = df_all.rename(columns=custom_labels)

## plot with plotly
pio.renderers.default='browser'
pd.options.plotting.backend = "plotly"
pio.templates.default = "plotly"
fig = px.line(
    df_all,
    x='TIMESTAMP',
    y=["et_l","et_le_l"],
    labels=custom_labels,
)

# fig = df_all.plot(x='TIMESTAMP',y=['SWTop','SWBottom','LWTop_cor','LWBottom_cor'], labels={"SWTop":"Incoming short wave radiation","SWBottom":"Outcoming short wave radiation","LWTop_cor":"Corrected incoming long wave radiation","LWBottom_cor":"Corrected outcoming long wave radiation"}) #,'Rn'])
#fig.update_layout(hovermode="x unified",xaxis_title=None,yaxis_title='Radiation [W/m²]')
## set date range maximum on end_date + 1
#if end_date==today:
#    fig.update_xaxes(range = [start_date,today])
#else:
#    fig.update_xaxes(range = [start_date,end_date + datetime.timedelta(days=1)])

## create simple dashboard
st.plotly_chart(fig, use_container_width=True)

## to do:
## plot Rn as well --> is also stored in crn4_data file instead of in crn4 file 

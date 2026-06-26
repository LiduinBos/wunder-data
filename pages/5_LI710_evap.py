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
import numpy as np

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
pars2 = "LI710all"

## account credentials of ftp server from where data will be downloaded
username = 'liduin'
password = 'WunDer@2024;'

# Download data files
# by making use of the requests python package
# and for the selected date range
df_all = pd.DataFrame()
i=0
for date in daterange:
    # choose correct pars depending on the date
    if date > "20250920":   # if your date is a string in YYYYMMDD format
        pars_used = pars2
    else:
        pars_used = pars

    url = (
        "http://liduin:WunDer@2024;@majisysdemo.itc.utwente.nl/"
        "wunder/logger_files/Wenumseveld_EC/"
        "CR3000_Wenumseveld_" + pars_used + date + ".dat"
    )
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
# st.write(df_all.columns)

## determine Makkink ET based on weather station data

def slope_vapour_pressure_curve(T):
    """
    Slope of saturation vapour pressure curve.
    T in °C.
    Output in kPa/°C.
    """
    es = 0.6108 * np.exp((17.27 * T) / (T + 237.3))
    delta = 4098 * es / ((T + 237.3) ** 2)
    return delta


def makkink_daily_et0(tmean, rs_mj_m2_day):
    """
    Makkink reference ET [mm/day].

    tmean: daily mean air temperature [°C]
    rs_mj_m2_day: daily incoming global radiation [MJ/m²/day]
    """
    gamma = 0.066  # kPa/°C, approximate near sea level
    lambda_v = 2.45  # MJ/kg

    delta = slope_vapour_pressure_curve(tmean)

    et0 = 0.65 * (delta / (delta + gamma)) * (rs_mj_m2_day / lambda_v)

    # avoid negative values
    return et0.clip(lower=0)

# Download data file (gathered by API call performed by UTwente and stored in csv)
# by making use of the requests python package
# and for the selected date range
url = "http://majisysdemo.itc.utwente.nl/wunder/get7days.py?location=z6-08820"
## download url
urlData = requests.get(url).content
## transform requests format to pandas
rawData_meteo = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
## remove header lines (1 and 2, keep 0 since this includes the abbreviation of the parameters)
df_meteo = rawData_meteo.drop([0]).reset_index(drop=True)
st.write(df_meteo.columns)

## determine 30 min aggregated data
df_meteo['datetime'] = pd.to_datetime(df_meteo['Date'])
df_meteo.set_index('datetime', inplace=True)

df_meteo['Air Temperature observation'] = pd.to_numeric(df_meteo['Air Temperature observation'], errors='coerce')
df_meteo_Ta = df_meteo.resample('d')['Air Temperature observation'].mean()
df_meteo['Radiation observation'] = pd.to_numeric(df_meteo['Radiation observation'], errors='coerce')
df_meteo_Rg_mj_m2 = df_meteo.resample('d')['Radiation observation'].mean()*(86400/1000000)

TEMP_COL = "Air Temperature observation"        # change if needed
RAD_COL = "Global radiation observation"        # change if needed; assumed W/m²

df_meteo_mak = makkink_daily_et0(df_meteo_Ta, df_meteo_Rg_mj_m2)

## ----------------------
## start plotting
## ----------------------
required_cols = {"et_l", "le_l", "TIMESTAMP"}

if not df_all.empty and required_cols.issubset(df_all.columns):
    
    df_all['et_l'] = df_all['et_l'].replace(['NAN', 9999999], pd.NA)
    df_all['le_l'] = df_all['le_l'].replace(9999999, pd.NA)

    df_all['et_l'] = pd.to_numeric(df_all['et_l'], errors='coerce')
    df_all['et_le_l'] = (pd.to_numeric(df_all['le_l'], errors='coerce') * 0.035)/48.0
    # st.write(df_all['et_l'])
    custom_labels = {
        "et_l": "evaporation [mm/day]",
        "et_le_l": "converted latent heat [mm/day]",
    }

    df_long = df_all.melt(
        id_vars='TIMESTAMP',
        value_vars=["et_l", "et_le_l"],
        var_name='variable',
        value_name='value'
    )

    df_long['variable'] = df_long['variable'].map(custom_labels)

    fig = px.line(
        df_long,
        x='TIMESTAMP',
        y='value',
        color='variable',
        labels={
            'TIMESTAMP': 'Date',
            'value': 'Evaporation [mm/30min]',
            'variable': 'Legend'
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    df_all['TIMESTAMP'] = pd.to_datetime(df_all['TIMESTAMP'])
    df_all = df_all.set_index('TIMESTAMP')
    df_daily = df_all[['et_l', 'et_le_l']].resample('D').sum()

    df_daily['et_mak'] = df_meteo_mak

    st.subheader("Daily evapotranspiration sum")
    
    st.dataframe(
        df_daily.reset_index().rename(columns={
            "TIMESTAMP": "Date",
            "et_l": "ET (eddypro) [mm/day]",
            "et_le_l": "ET (LE converted) [mm/day]"
        }),
        use_container_width=True
    )


else:
    st.warning("⚠️ No ET / LE data found for the selected date range.")

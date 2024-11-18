import streamlit as st
import requests
import pandas as pd
import json
import datetime
import time

import plotly.io as pio
import plotly.express as px

# Streamlit app title
st.title('ZENTRA Cloud API Caller')

# Set start and end date with date picker
today = datetime.date.today()
history = today - datetime.timedelta(days=7)
start_date = st.date_input(
    'Start date', history, min_value=datetime.datetime(2023, 12, 1), max_value=today - datetime.timedelta(days=2)
)
end_date_max = today - datetime.timedelta(days=1)
end_date = st.date_input(
    'End date', end_date_max, min_value=datetime.datetime(2023, 12, 1), max_value=end_date_max
)
if start_date < end_date:
    pass
else:
    st.error('Error: End date must fall after start date.')

# Device Serial Number
stnr = 'z6-08820'

# Function to make API requests with authorization token
def get_with_credentials(tok, uri, **kwargs):
    token = tok if tok.lower().startswith("token") else f"Token {tok}"
    headers = {"Authorization": token}
    return requests.get(uri, headers=headers, **kwargs)

# Function to call the API and handle pagination with delay
def get_readings_response_paginated(sn, start_date, end_date, token, **extra_kwargs_for_endpoint):
    server = extra_kwargs_for_endpoint.get("server", "https://zentracloud.com")
    url = f"{server}/api/v4/get_readings/"
    
    # Initialize variables for pagination
    page_num = 1
    per_page = 100  # Number of records per page
    all_readings = []  # This list will hold all the data collected from all pages

    while True:
        # Prepare request parameters
        default_args = {
            'output_format': "json",
            'per_page': per_page,
            'page_num': page_num,
            'sort_by': 'asc',
            'start_date': start_date,
            'end_date': end_date
        }
        data = {**default_args, **extra_kwargs_for_endpoint, "device_sn": sn}
        
        # Make the API request
        response = get_with_credentials(token, url, params=data)

        # Break the loop if the response is not OK
        if not response.ok:
            st.error(f"API request failed on page {page_num}: {response.status_code} - {response.text}")
            if response.status_code == 429:
                st.warning("Rate limit reached. Waiting 60 seconds before retrying...")
                time.sleep(60)  # Delay to handle rate limit
                continue  # Retry the same page after the delay
            break

        # Parse the JSON response
        json_data = response.json()
        air_temp_readings = json_data.get("data", {}).get("Air Temperature", [])

        if not air_temp_readings:
            # No more data to fetch
            break
        
        # Append current page's readings to the list
        all_readings.extend(air_temp_readings)

        # Increment the page number for the next iteration
        page_num += 1

    return all_readings  # Return all data collected after all pages

# Function to extract and normalize "Air Temperature" data
def extract_air_temperature_data(all_readings):
    extracted_data = []

    for entry in all_readings:
        metadata = entry.get("metadata", {})
        readings = entry.get("readings", [])
        
        # Combine metadata with each reading
        for reading in readings:
            combined = {**metadata, **reading}
            extracted_data.append(combined)
    
    if extracted_data:
        return pd.DataFrame(extracted_data)  # Return the combined data as a DataFrame
    else:
        st.warning("No 'Air Temperature' readings found in the data.")
        return pd.DataFrame()

# Function to retrieve and parse "Air Temperature" readings into a DataFrame
def get_air_temperature_dataframe(sn, start_date, end_date, token, **extra_kwargs_for_endpoint):
    all_readings = get_readings_response_paginated(sn, start_date, end_date, token, **extra_kwargs_for_endpoint)
    if all_readings:
        return extract_air_temperature_data(all_readings)
    return pd.DataFrame()

# Fill in your token, device serial number, and date range
tok = "f9e6d698624c76340adde78b22a9c6ff514c6e42"
sn = stnr
server = "https://zentracloud.com"

# Make API Call Button
if st.button('Make API Call'):
    try:
        # Retrieve data as DataFrame
        df = get_air_temperature_dataframe(sn, start_date, end_date, tok, server=server)

        if not df.empty:
            st.success('API Call Successful!')
            st.dataframe(df)  # Display DataFrame in Streamlit

            ## plot with plotly
            pio.renderers.default='browser'
            pd.options.plotting.backend = "plotly"
            fig = df.plot(x='datetime',y='value')
            fig.update_layout(hovermode="x unified",xaxis_title=None,yaxis_title='Atmospheric temperature [*C]')
            ## set date range maximum on end_date + 1
            if end_date==today:
                fig.update_xaxes(range = [start_date,today])
            else:
                fig.update_xaxes(range = [start_date,end_date + datetime.timedelta(days=1)])
            
            ## create simple dashboard
            st.plotly_chart(fig)
        
        else:
            st.warning('No data retrieved. Check date range or device serial number.')
    except Exception as e:
        st.error(f'An error occurred: {e}')



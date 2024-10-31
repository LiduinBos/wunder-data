import streamlit as st
import requests
import pandas as pd
import json

# Streamlit app title
st.title('ZENTRA Cloud API Caller')

# Device Serial Number
stnr = 'z6-08820'

# Function to make API requests with authorization token
def get_with_credentials(tok, uri, **kwargs):
    token = tok if tok.lower().startswith("token") else f"Token {tok}"
    headers = {"Authorization": token}
    return requests.get(uri, headers=headers, **kwargs)

# Function to call the API and get readings
def get_readings_response(sn, start_date, end_date, **extra_kwargs_for_endpoint):
    server = extra_kwargs_for_endpoint.get("server", "https://zentracloud.com")
    url = f"{server}/api/v4/get_readings/"

    default_args = {
        'output_format': "json",
        'per_page': 1,
        'page_num': 1,
        'sort_by': 'desc',
        'start_date': start_date,
        'end_date': end_date
    }
    data = {**default_args, **extra_kwargs_for_endpoint, "device_sn": sn}
    tok = extra_kwargs_for_endpoint.pop("token", "")
    return get_with_credentials(tok, url, params=data)

# Parse and Display JSON Data in DataFrame
def get_readings_dataframe(sn, start_date, end_date, **extra_kwargs_for_endpoint):
    res = get_readings_response(sn, start_date, end_date, **extra_kwargs_for_endpoint)
    if res.ok:
        try:
            data = res.json().get("data", [])
            st.write("Raw Data:", data)  # Display raw data to inspect
            # Normalize and handle any nested or irregular fields
            df = pd.json_normalize(data, errors='ignore')
            return df
        except json.JSONDecodeError:
            st.error("Error decoding JSON response.")
    else:
        st.error(f"Failed to retrieve data: {res.status_code} - {res.text}")
    return pd.DataFrame()

# Fill in your token, device serial number, and date range
tok = "f9e6d698624c76340adde78b22a9c6ff514c6e42"
sn = stnr
start_date = "2024-04-01 00:00:00"
end_date = "2024-04-02 00:00:00"

# Server URL
server = "https://zentracloud.com"

# Make API Call Button
if st.button('Make API Call'):
    try:
        # Retrieve data as DataFrame
        df = get_readings_dataframe(sn, start_date, end_date, token=tok, server=server)

        # Check if DataFrame is not empty
        if not df.empty:
            st.success('API Call Successful!')
            st.write(df)  # Display DataFrame in Streamlit
        else:
            st.warning('No data retrieved. Check date range or device serial number.')
    except Exception as e:
        st.error(f'An error occurred: {e}')

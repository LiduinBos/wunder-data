import streamlit as st
import requests
import pandas as pd
import json
import datetime

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

# Function to call the API and get readings
def get_readings_response(sn, start_date, end_date, **extra_kwargs_for_endpoint):
    server = extra_kwargs_for_endpoint.get("server", "https://zentracloud.com")
    url = f"{server}/api/v4/get_readings/"

    default_args = {
        'output_format': "json",
        'per_page': 100,  # Adjust as needed
        'page_num': 1,
        'sort_by': 'desc',
        'start_date': start_date,
        'end_date': end_date
    }
    data = {**default_args, **extra_kwargs_for_endpoint, "device_sn": sn}
    tok = extra_kwargs_for_endpoint.pop("token", "")
    return get_with_credentials(tok, url, params=data)

# Function to extract and normalize JSON data
def extract_data(json_data):
    # Initialize an empty list to store processed records
    extracted_data = []

    # Loop through "Air Temperature" entries in JSON data
    for entry in json_data.get("Air Temperature", []):
        metadata = entry.get("metadata", {})
        readings = entry.get("readings", [])
        
        # Combine metadata with each reading
        for reading in readings:
            combined = {**metadata, **reading}
            extracted_data.append(combined)
    
    # Convert to DataFrame
    st.write(pd.DataFrame(extracted_data))
    return pd.DataFrame(extracted_data)

# Function to parse API response and extract data
def get_readings_dataframe(sn, start_date, end_date, **extra_kwargs_for_endpoint):
    res = get_readings_response(sn, start_date, end_date, **extra_kwargs_for_endpoint)
    if res.ok:
        try:
            json_data = res.json()  # Get full JSON response
            st.write(json_data)
            # Extract and normalize JSON data
            df = extract_data(json_data)
            st.write(df)
            return df
        except json.JSONDecodeError:
            st.error("Error decoding JSON response.")
    else:
        st.error(f"Failed to retrieve data: {res.status_code} - {res.text}")
    return pd.DataFrame()

# Fill in your token, device serial number, and date range
tok = "f9e6d698624c76340adde78b22a9c6ff514c6e42"
sn = stnr
server = "https://zentracloud.com"

# Make API Call Button
if st.button('Make API Call'):
    try:
        # Retrieve data as DataFrame
        df_extract = get_readings_dataframe(sn, start_date, end_date, token=tok, server=server)
        st.write(df_extract)

        # Check if DataFrame is not empty
        if not df_extract.empty:
            st.success('API Call Successful!')
            st.dataframe(df_extract)  # Display DataFrame in Streamlit
        else:
            st.warning('No data retrieved. Check date range or device serial number.')
    except Exception as e:
        st.error(f'An error occurred: {e}')

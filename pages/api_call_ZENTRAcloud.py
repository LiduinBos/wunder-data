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
history = today - datetime.timedelta(days=4)
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

# Function to handle pagination and minimize requests
def get_readings_response_eff(sn, start_date, end_date, token, variables, **extra_kwargs_for_endpoint):
    server = extra_kwargs_for_endpoint.get("server", "https://zentracloud.com")
    url = f"{server}/api/v4/get_readings/"
    
    # Request parameters for larger data chunks
    default_args = {
        'output_format': "json",
        'per_page': 1000,  # Request up to 1000 records per page
        'page_num': 1,
        'sort_by': 'asc',
        'start_date': start_date,
        'end_date': end_date
    }
    
    data = {**default_args, **extra_kwargs_for_endpoint, "device_sn": sn}
    all_readings = {var: [] for var in variables}  # Dictionary to hold all data for each variable

    # Loop for pagination (we only expect 1 page now due to per_page=1000)
    page_num = 1
    while True:
        data['page_num'] = page_num
        response = get_with_credentials(token, url, params=data)

        # Handle rate limit error (429)
        if response.status_code == 429:
            st.warning("Rate limit reached. Waiting 60 seconds before retrying...")
            time.sleep(60)  # Wait for 60 seconds before retrying the request
            continue  # Retry the request

        # Check for non-OK responses
        if not response.ok:
            st.error(f"API request failed: {response.status_code} - {response.text}")
            break

        # Parse the JSON response
        json_data = response.json()

        # Loop over the selected variables and extract data for each one
        for var in variables:
            readings = json_data.get("data", {}).get(var, [])
            if readings:
                all_readings[var].extend(readings)

        # Break the loop if there is no more data
        if all(len(readings) == 0 for readings in all_readings.values()):
            break
        
        page_num += 1  # Increment page number for next request

    return all_readings

# Function to extract and normalize "Air Temperature" data
def extract_data(all_readings,variables):
    extracted_data = []
    
    for var in variables:
        readings = all_readings.get(var, [])
        if readings:
            for entry in readings:
                metadata = entry.get("metadata", {})
                data_readings = entry.get("readings", [])
                # Combine metadata with each reading for each variable
                for reading in data_readings:
                    combined = {**metadata, **reading, 'variable': var}
                    extracted_data.append(combined)
    
    if extracted_data:
        return pd.DataFrame(extracted_data)  # Return the combined data as a DataFrame
    else:
        st.warning("No 'Air Temperature' readings found in the data.")
        return pd.DataFrame()

# Function to retrieve and parse "Air Temperature" readings into a DataFrame
def get_data_dataframe(sn, start_date, end_date, token, variables, **extra_kwargs_for_endpoint):
    all_readings = get_readings_response_eff(sn, start_date, end_date, token, variables, **extra_kwargs_for_endpoint)
    
    if all_readings:
        return extract_data(all_readings, variables)
    return pd.DataFrame()

# Fill in your token, device serial number, and date range
tok = "f9e6d698624c76340adde78b22a9c6ff514c6e42"
sn = stnr
server = "https://zentracloud.com"

# List of variables to retrieve (e.g., 'Air Temperature', 'Precipitation')
variables = ['Air Temperature', 'Precipitation']

# Make API Call Button
if st.button('Make API Call'):
    try:
        # Retrieve data as DataFrame
        df = get_data_dataframe(sn, start_date, end_date, tok, variables, server=server)

        if not df.empty:
            st.success('API Call Successful!')
            st.dataframe(df)  # Display DataFrame in Streamlit
            st.write(df)

            # Plot the Air Temperature data
            if 'datetime' in df.columns and 'value' in df.columns:
                # Convert 'datetime' column to pandas datetime type
                df['datetime'] = pd.to_datetime(df['datetime'])

                # Create a line plot using Plotly Express
                fig = px.line(df, x='datetime', y='value', title='Air Temperature Over Time',
                              labels={'datetime': 'Timestamp', 'value': 'Temperature (°C)'})
                st.plotly_chart(fig)  # Display Plotly chart in Streamlit
        else:
            st.warning('No data retrieved. Check date range or device serial number.')
    except Exception as e:
        st.error(f'An error occurred: {e}')

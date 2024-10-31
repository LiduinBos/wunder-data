import streamlit as st
import requests

# Streamlit app title
st.title('ZENTRA Cloud API Caller')

# Input for API endpoint and data
api_url = st.text_input('API Endpoint URL', 'https://api.zentra.com/v1/your-endpoint')
data_input = st.text_area('Request Data (JSON)', '{"key": "value"}')

if st.button('Make API Call'):
    try:
        # Convert the input data to a dictionary
        data = eval(data_input)  # Use json.loads(data_input) in production for safety
        headers = {
            'Authorization': 'Bearer YOUR_TOKEN',
            'Content-Type': 'application/json'
        }

        # Make the API call
        response = requests.post(api_url, headers=headers, json=data)

        # Check the response
        if response.status_code == 200:
            st.success('API Call Successful!')
            st.json(response.json())
        else:
            st.error(f'Error: {response.status_code} - {response.text}')

    except Exception as e:
        st.error(f'An error occurred: {e}')


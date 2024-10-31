import streamlit as st
import requests
import pandas

# Streamlit app title
st.title('ZENTRA Cloud API Caller')

stnr = 'z6-08820'

# Input for API endpoint and data
# api_url = st.text_input('API Endpoint URL', 'https://zentracloud.com/api/v4/'+stnr)
# data_input = st.text_area('Request Data (JSON)', '{"key": "f9e6d698624c76340adde78b22a9c6ff514c6e42"}')

def get_with_credentials(tok, uri, **kwargs):
   # just in case we forget to put "Token MyToken"
   token = tok if tok.lower().startswith("token") else f"Token {tok}"
   headers = {"Authorization": token}
   return requests.get(uri, headers=headers, **kwargs)

def get_readings_response(sn, start_date, end_date, **extra_kwargs_for_endpoint):
    server = extra_kwargs_for_endpoint.get("server", "https://zentracloud.com")
    url = f"{server}/api/v4/get_readings/"

    default_args = {
        'output_format': "df",
        'per_page': 1,
        'page_num': 1,
        'sort_by': 'desc',
        'start_date': start_date,
        'end_date': end_date
    }
    data = {**default_args, **extra_kwargs_for_endpoint, "device_sn": sn}
    tok = extra_kwargs_for_endpoint.pop("token", "")
    return get_with_credentials(tok, url, params=data)

def get_readings_dataframe(sn,start_date,end_date,**extra_kwargs_for_endpoint):
    res = get_readings_response(sn,start_date,end_date,**extra_kwargs_for_endpoint)
    if(res.ok):
        data = res.json()
        return pandas.DataFrame(**json.loads(data["data"]))
    return res

#fill in your token, device serial number and start and end dates here.
tok = "f9e6d698624c76340adde78b22a9c6ff514c6e42"
sn="z6-"+stnr
start_date="2024-04-01 00:00:00"
end_date="2024-04-02 00:00:00"

#specify the server here.
server="https://zentracloud.com"

if st.button('Make API Call'):
    try:
       # data = eval(data_input) 
       # df = get_readings_dataframe(sn, start_date, end_date, token=tok, server=server)
       # print(df)
       response = get_readings_response(sn,start_date,end_date,token=tok, server=server)

       # Check the response
       if response.status_code == 200:
           st.success('API Call Successful!')
           st.json(response.json())
       else:
           st.error(f'Error: {response.status_code} - {response.text}')

    except Exception as e:
        st.error(f'An error occurred: {e}')

# if st.button('Make API Call'):
#     try:
#         # Convert the input data to a dictionary
#         data = eval(data_input)  # Use json.loads(data_input) in production for safety
#         headers = {
#             'Authorization': 'f9e6d698624c76340adde78b22a9c6ff514c6e42',
#             # 'Content-Type': 'application/json'
#         }

#         # Make the API call
#         response = requests.get(api_url, headers=headers, json=data)

#         # Check the response
#         if response.status_code == 200:
#             st.success('API Call Successful!')
#             st.json(response.json())
#         else:
#             st.error(f'Error: {response.status_code} - {response.text}')

#     except Exception as e:
#         st.error(f'An error occurred: {e}')

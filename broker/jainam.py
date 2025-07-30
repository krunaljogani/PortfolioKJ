import requests
import streamlit as st
import pandas as pd

# Load credentials from Streamlit secrets
API_KEY = st.secrets["jainam_api"]["key"]
SECRET_KEY = st.secrets["jainam_api"]["secret"]

def jainam_login(client_code, password, dob):
    url = "https://protrade.jainam.in/api/v2/login"

    headers = {
        "X-API-Key": API_KEY,
        "X-API-Secret": SECRET_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "clientcode": client_code,
        "password": password,
        "dob": dob  # Format: YYYY-MM-DD
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        return data["data"]["token"]  # You may store this for future requests
    else:
        st.error(f"Login failed: {response.text}")
        return None
        
def get_holdings(token):
    url = JAINAM_BASE_URL + "holding"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)
    return res.json() if res.status_code == 200 else []

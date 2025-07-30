import streamlit as st
import requests

def jainam_login(client_code, password, dob):
    try:
        API_KEY = st.secrets["jainam_api"]["key"]
        SECRET_KEY = st.secrets["jainam_api"]["secret"]
    except Exception as e:
        st.error(f"Error loading API credentials: {e}")
        return None

    url = "https://protrade.jainam.in/api/v2/login"
    headers = {
        "X-API-Key": API_KEY,
        "X-API-Secret": SECRET_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "clientcode": client_code,
        "password": password,
        "dob": dob
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json().get("data", {}).get("token")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed for {client_code}: {e}")
        return None
        
def get_holdings(token):
    url = JAINAM_BASE_URL + "holding"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)
    return res.json() if res.status_code == 200 else []

import streamlit as st
import requests
import hashlib

def generate_checksum(user_id, auth_code, api_secret):
    base_string = user_id + auth_code + api_secret
    return hashlib.sha256(base_string.encode()).hexdigest()

def jainam_sso_login(user_id, auth_code):
    api_secret = st.secrets["jainam_api"]["api_secret"]
    checksum = generate_checksum(user_id, auth_code, api_secret)

    payload = {
        "checkSum": checksum
    }

    url = "https://protrade.jainam.in/omt/auth/sso/vendor/getUserDetails"

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"SSO login failed for {user_id}: {e}")
        return None
        
def get_holdings(token):
    url = JAINAM_BASE_URL + "holding"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)
    return res.json() if res.status_code == 200 else []

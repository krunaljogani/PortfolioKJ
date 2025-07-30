import streamlit as st
import pandas as pd
import requests
import hashlib
from broker import jainam, zerodha, nuvama_mock
import json
from broker.zerodha import ZerodhaClient, load_tokens, save_tokens

st.set_page_config(page_title="Multi-Broker Portfolio", layout="wide")
st.title("📊 Multi-Broker Portfolio Tracker")
st.write("Loaded secret:", st.secrets["jainam_api"]["secret"])
api_secret = st.secrets["jainam_api"]["secret"]
tabs = st.tabs(["Jainam", "Zerodha", "Nuvama"])



with tabs[0]: 
    APP_CODE = "DDuniRrYMgkPblF"
    REDIRECT_URL = "https://portfolioKJ.streamlit.app/"
    JAINAM_LOGIN_URL = f"https://protrade.jainam.in/?appcode={APP_CODE}&redirect_url={REDIRECT_URL}"

# --- Get query params from redirect ---
user_id = st.query_params.get("userId", [None])[5]
auth_code = st.query_params.get("authCode", [None])[0]

# --- Function to get user session ---
def get_jainam_session(user_id, auth_code, api_secret):
    raw_string = user_id + auth_code + api_secret
    st.write(user_id)
    st.write(auth_code)
    st.write(api_secret)
    st.write(raw_string)
    checksum = hashlib.sha256(raw_string.encode()).hexdigest()
    st.write(checksum)
    res = requests.post(
        "https://protrade.jainam.in/omt/auth/sso/vendor/getUserDetails",
        json={"checkSum": checksum},
        headers={"Content-Type": "application/json"}
    )
    if res.status_code == 200:
        return res.json()
    else:
        st.error(f"Session fetch failed: {res.status_code} - {res.text}")
        
        return None
def get_holdings(user_session):
    headers = {"Authorization": user_session}
    res = requests.get(
        "https://protrade.jainam.in/oms/scrip/holding",
        headers=headers
    )
    if res.status_code == 200:
        return res.json()
    else:
        st.error(f"Holdings fetch failed: {res.status_code} - {res.text}")
        return None

st.title("📊 Jainam Login Demo")

if user_id and auth_code:
    st.success("🔐 Auth token received from Jainam")
    api_secret = st.secrets["jainam_api"]["secret"]
    session_response = get_jainam_session(user_id, auth_code, api_secret)
    if session_response and "userSession" in session_response:
        user_session = session_response["userSession"]
        st.success("✅ Session token retrieved")
        st.code(user_session, language="text")

        holdings = get_holdings(user_session)
        if holdings:
            st.subheader("📈 Holdings")
            st.json(holdings)
    else:
        st.error("❌ Failed to get session from Jainam")
else:
    if st.button("🔐 Login to Jainam"):
        st.markdown(f"[🔐 Click here to login to Jainam]({JAINAM_LOGIN_URL})")
with tabs[1]:
    st.header("🔐 Zerodha")
    tokens = load_tokens()
    email = st.selectbox("Zerodha User", list(tokens.keys()) + ["New user"])

    if email == "New user":
        st.warning("Use terminal to complete login")
        api_key = st.text_input("API Key", "pzgl6qu9ma64bt53")
        api_secret = st.text_input("API Secret", type="password")
        zc = ZerodhaClient(api_key, api_secret)
        login_url = zc.get_login_url()
        st.markdown(f"[Login to Zerodha]({login_url})")
        request_token = st.text_input("Paste request_token after login:")
        if request_token:
            session_data = zc.generate_session(request_token)
            tokens[session_data["user_id"]] = {
                "access_token": session_data["access_token"],
                "public_token": session_data["public_token"]
            }
            save_tokens(tokens)
            st.success("Zerodha token saved.")
    else:
        zc = ZerodhaClient("pzgl6qu9ma64bt53", "<YOUR_SECRET>")
        zc.set_access_token(tokens[email]["access_token"])
        holdings = zc.get_holdings()
        st.dataframe(pd.DataFrame(holdings))

with tabs[2]:
    st.header("📦 Nuvama (Mock Data)")
    st.dataframe(pd.DataFrame(nuvama_mock.get_mock_holdings()))

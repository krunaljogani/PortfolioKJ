import streamlit as st
import pandas as pd
from broker import jainam, zerodha, nuvama_mock
import json
from broker.zerodha import ZerodhaClient, load_tokens, save_tokens

st.set_page_config(page_title="Multi-Broker Portfolio", layout="wide")
st.title("📊 Multi-Broker Portfolio Tracker")
api_secret = st.secrets["jainam_api"]["secret"]
tabs = st.tabs(["Jainam", "Zerodha", "Nuvama"])



with tabs[0]:
    
   APP_CODE = "DDuniRrYMgkPblF"
REDIRECT_URL = "https://portfolioKJ.streamlit.app"
JAINAM_LOGIN_URL = f"https://protrade.jainam.in/?appcode={APP_CODE}&redirect_url={REDIRECT_URL}"

# --- Get query params from redirect ---
user_id = st.query_params.get("userId", [None])[0]
auth_code = st.query_params.get("authCode", [None])[0]

# --- Function to get user session ---
def get_jainam_session(user_id, auth_code, api_secret):
    if not all([user_id, auth_code, api_secret]):
        return None
    raw_string = user_id + auth_code + api_secret
    checksum = hashlib.sha256(raw_string.encode()).hexdigest()

    try:
        response = requests.post(
            "https://protrade.jainam.in/omt/auth/sso/vendor/getUserDetails",
            json={"checkSum": checksum}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Exception occurred: {str(e)}")
        return None

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

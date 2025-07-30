import streamlit as st
import pandas as pd
from broker import jainam, zerodha, nuvama_mock
import json
from broker.zerodha import ZerodhaClient, load_tokens, save_tokens
from broker.jainam import jainam_login

st.set_page_config(page_title="Multi-Broker Portfolio", layout="wide")
st.title("📊 Multi-Broker Portfolio Tracker")

tabs = st.tabs(["Jainam", "Zerodha", "Nuvama"])

with tabs[0]:

    
    for label, creds in st.secrets["jainam_sso"].items():
        st.subheader(f"🔑 Account: {label}")
        result = jainam.jainam_sso_login(creds["user_id"], creds["auth_code"])
        if result:
        st.success("Logged in to Jainam")
        holdings = jainam.get_holdings(token)
        st.dataframe(pd.DataFrame(holdings))
        else:
        st.error("Login failed")

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

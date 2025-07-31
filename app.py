import streamlit as st
import pandas as pd
import requests
import hashlib
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

query_params = st.query_params
user_id = query_params.get("userId")
auth_code = query_params.get("authCode")

if user_id is not None:
    user_id = str(user_id)
if auth_code is not None:
    auth_code = str(auth_code)

def get_jainam_session(user_id, auth_code, api_secret):
    raw_string = str(user_id) + str(auth_code) + str(api_secret)
    checksum = hashlib.sha256(raw_string.encode()).hexdigest()

    res = requests.post(
        "https://protrade.jainam.in/omt/auth/sso/vendor/getUserDetails",
        json={"checkSum": checksum}
    )
    if res.status_code == 200:
        return res.json()
    else:
        st.error(f"Session fetch failed: {res.status_code} - {res.text}")
        return None
        
def get_holdings(user_session):
    BASE_URL_HOLDINGS = "https://protrade.jainam.in/"
    url = f"{BASE_URL_HOLDINGS}api/ho-rest/holdings"

    headers = {
        "Authorization": f"Bearer {user_session}"
    }

    res = requests.get(url, headers=headers)

    # Ensure we received a JSON response
    content_type = res.headers.get("Content-Type", "")
    if "application/json" not in content_type:
        st.error(f"Unexpected response format:\n{res.text[:500]}")
        return None

    try:
        data = res.json()
    except Exception as e:
        st.error(f"Failed to parse JSON response:\n{res.text[:500]}")
        return None

    if data.get("status") == "Ok":
        holdings = data.get("result", [{}])[0].get("holdings")
        rows = []
    
        for item in holdings:
            #val = item.get("holdingVal", {})
            #ex_details = val.get("exDetails", [])
            
            rows.append({
                "Share": item.get("symbol", [{}])[0].get("tradingSymbol"),
                "Total Qty": float(item.get("netQty")),
                "Current Price": float(item.get("symbol", [{}])[0].get("ltp")),
                "Buy Price": float(item.get("buyPrice")),
                "Buy Value": float(item.get("buyPrice"))*float(item.get("netQty")),
                "Current Value": float(item.get("symbol", [{}])[0].get("ltp"))*float(item.get("netQty")),
                "Day PnL": 0,
                "Total PnL": float(item.get("symbol", [{}])[0].get("ltp"))*float(item.get("netQty")) - float(item.get("buyPrice"))*float(item.get("netQty")),
                "Broker":"Jainam - " + user_id
            })
        
        df = pd.DataFrame(rows)
        # ➕ Add Total Row
        total_row = {
            "Share": "TOTAL",
            "Buy Value": df["Buy Value"].sum(),
            "Current Value": df["Current Value"].sum(),
            "Day PnL": df["Day PnL"].sum(),
            "Total PnL": df["Total PnL"].sum()
        }

        df.loc[len(df)] = total_row  # Append the total row
        st.dataframe(df, use_container_width=True) 
        #return data.get("result", [])
    else:
        st.error(f"API Error: {data.get('message')}")
        return None


st.title("📊 Jainam Login Demo")

if user_id and auth_code:
    #st.success("🔐 Auth token received from Jainam")
    api_secret = st.secrets["jainam_api"]["secret"]
    session_response = get_jainam_session(user_id, auth_code, api_secret)
    if session_response and session_response.get("result") and "accessToken" in session_response["result"][0]:
        user_session = session_response["result"][0]["accessToken"]
        #st.success("✅ Session token retrieved")
        #st.code(user_session, language="text")
        holdings = get_holdings(user_session)
        if holdings:
            st.subheader("📈 Holdings")
            st.json(holdings)
    else:
        st.error("❌ Failed to get session from Jainam")
        st.write(session_response)
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

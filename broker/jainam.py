import requests

JAINAM_BASE_URL = "https://protrade.jainam.in/api-client/"

def login_jainam(client_code, password, dob):
    url = JAINAM_BASE_URL + "login"
    payload = {
        "clientcode": client_code,
        "password": password,
        "dob": dob
    }
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        return res.json().get("access_token")
    return None

def get_holdings(token):
    url = JAINAM_BASE_URL + "holding"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)
    return res.json() if res.status_code == 200 else []

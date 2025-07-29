from kiteconnect import KiteConnect
import json

def load_tokens(filepath="data/zerodha_tokens.json"):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except:
        return {}

def save_tokens(tokens, filepath="data/zerodha_tokens.json"):
    with open(filepath, "w") as f:
        json.dump(tokens, f, indent=2)

class ZerodhaClient:
    def __init__(self, api_key, api_secret):
        self.kite = KiteConnect(api_key=api_key)
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = None

    def get_login_url(self):
        return self.kite.login_url()

    def generate_session(self, request_token):
        data = self.kite.generate_session(request_token, api_secret=self.api_secret)
        self.kite.set_access_token(data["access_token"])
        self.session = data
        return data

    def set_access_token(self, access_token):
        self.kite.set_access_token(access_token)

    def get_holdings(self):
        return self.kite.holdings()

    def get_positions(self):
        return self.kite.positions()

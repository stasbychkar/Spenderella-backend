import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

client_id = os.getenv("PLAID_CLIENT_ID")
secret = os.getenv("PLAID_SECRET")
env = os.getenv("PLAID_ENV")

base_url = f"https://{env}.plaid.com"

def create_link_token():
    url = f"{base_url}/link/token/create"
    headers = {"Content-Type": "application/json"}
    data = {
        "client_id": client_id,
        "secret": secret,
        "user": {"client_user_id": "user123"},
        "client_name": "Spenderella",
        "products": ["transactions"],
        "country_codes": ["US"],
        "language": "en",
    }
    res = requests.post(url, json=data, headers=headers)
    return res.json()

def exchange_public_token(public_token):
    url = f"{base_url}/item/public_token/exchange"
    headers = {"Content-Type": "application/json"}
    data = {
        "client_id": client_id,
        "secret": secret,
        "public_token": public_token,
    }
    res = requests.post(url, json=data, headers=headers)
    return res.json()

def get_transactions(access_token):
    url = f"{base_url}/transactions/get"
    headers = {"Content-Type": "application/json"}

    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')

    data = {
        "client_id": client_id,
        "secret": secret,
        "access_token": access_token,
        "start_date": start_date,
        "end_date": end_date
    }
    res = requests.post(url, json=data, headers=headers)
    return res.json()

# def sync_transactions(item_id):
#     url = f"{base_url}/transactions/sync"
#     headers = {"Content-Type": "application/json"}
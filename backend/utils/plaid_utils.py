import os
import requests
import plaid
from plaid import Configuration, ApiClient
from plaid.api import plaid_api
from dotenv import load_dotenv
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from datetime import datetime, timedelta
from backend.db import sessionlocal
from backend.models import BankItem, Transaction, Account
from backend.utils.crypto import decrypt

load_dotenv()

client_id = os.getenv("PLAID_CLIENT_ID")
secret = os.getenv("PLAID_SECRET")
env = os.getenv("PLAID_ENV")

# creating client using Plaid's SDK
configuration = Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': client_id,
        'secret': secret,
    }
)
api_client = ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

def create_link_token():
    response = plaid_client.link_token_create({
        'user': {'client_user_id': '1'}, # hardcoded internal user ID
        "client_name": "Spenderella",
        "products": ["transactions"],
        "country_codes": ["US"],
        "language": "en",
    })
    return response.to_dict()

def exchange_public_token(public_token):
    exchange_request = ItemPublicTokenExchangeRequest(public_token)
    exchange_response = plaid_client.item_public_token_exchange(exchange_request)
    # access_token = exchange_response['access_token']
    return exchange_response.to_dict()

def sync_accounts(access_token_encrypted: str):
    access_token = decrypt(access_token_encrypted)
    response = plaid_client.accounts_get(AccountsGetRequest(access_token=access_token))
    return response.accounts

def sync_transactions(access_token: str, cursor: str=None):
    request = TransactionsSyncRequest(
            access_token=access_token
        )
    response = plaid_client.transactions_sync(request)
    # transactions = response['added']
    
    while (response['has_more']):
        request = TransactionsSyncRequest(
            access_token=access_token,
            cursor=response['next_cursor']
        )
        response = plaid_client.transactions_sync(request)
        # transactions += response['added']
        repponse += response
    
    # for testing purposes
    # print(response)
    
    return response.to_dict()

def sync_all_transactions(user_id: int = 1): # hardcoded for now
    db = sessionlocal()
    bank_items = db.query(BankItem).filter_by(user_id=user_id).all()

    for item in bank_items:
        access_token_encrypted = item.access_token_encrypted
        cursor = item.cursor
        access_token = decrypt(access_token_encrypted)

        result = sync_transactions(access_token, cursor)

        for transaction in result["added"]:
            account = db.query(Account).filter_by(plaid_account_id=transaction['account_id']).first()
            account_id = account.id
            bank_item = db.query(BankItem).filter_by(id=account.bank_item_id).first()
            bank_item_id = bank_item.id

            exists = db.query(Transaction).filter_by(plaid_transaction_id=transaction["transaction_id"]).first()
            if exists: continue
            else:
                new_transaction = Transaction(
                    plaid_transaction_id = transaction['transaction_id'],
                    account_id=account_id,
                    plaid_account_id = transaction['account_id'],
                    user_id = user_id,
                    bank_item_id = bank_item_id,
                    merchant_name = transaction.get('merchant_name'),
                    name = transaction['name'],
                    amount = transaction['amount'],
                    payment_channel = transaction.get('payment_channel'),
                    iso_currency_code = transaction.get('iso_currency_code'),
                    personal_finance_category_primary = transaction.get("personal_finance_category", {}).get("primary"),
                    personal_finance_category_detailed = transaction.get("personal_finance_category", {}).get("detailed"),
                    date = transaction['date'],
                    authorized_date = transaction.get('authorized_date'),
                    pending = transaction['pending']
                )
                db.add(new_transaction)

        item.cursor = result["next_cursor"]
        db.commit()

    db.close()
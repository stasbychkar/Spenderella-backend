import os
import requests
import plaid
import logging
from plaid import Configuration, ApiClient
from plaid.api import plaid_api
from dotenv import load_dotenv
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from datetime import datetime, timedelta
from backend.db import sessionlocal
from backend.models import BankItem, Transaction, Account, DefaultCategory
from backend.utils.crypto import decrypt
from collections import defaultdict
from datetime import datetime, timedelta
from sqlalchemy import and_

load_dotenv()

client_id = os.getenv("PLAID_CLIENT_ID")
secret = os.getenv("PLAID_SECRET")
env = os.getenv("PLAID_ENV")

# Create client using Plaid's SDK
configuration = Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': client_id,
        'secret': secret,
    }
)
api_client = ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)
# ------------------------

# Set up logger
logger = logging.getLogger("plaid_calls")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("backend/logs/plaid_api_calls.log")
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
# Logging in the terminal
# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(formatter)
# logger.addHandler(stream_handler)

def log_plaid_call(endpoint_name, details=""):
    logger.info(f"PLAID API CALL: {endpoint_name} | {details}")
# ------------------------

def create_link_token():
    log_plaid_call("link_token_create")
    response = plaid_client.link_token_create({
        'user': {'client_user_id': '1'}, # hardcoded internal user ID
        "client_name": "Spenderella",
        "products": ["transactions"],
        "country_codes": ["US"],
        "language": "en",
        "webhook": "https://fa07-2601-600-9380-ca0-4dc5-8b48-1a4e-4b57.ngrok-free.app/webhook"
    })
    return response.to_dict()

def exchange_public_token(public_token):
    log_plaid_call("item_public_token_exchange")
    exchange_request = ItemPublicTokenExchangeRequest(public_token)
    exchange_response = plaid_client.item_public_token_exchange(exchange_request)
    # access_token = exchange_response['access_token']
    return exchange_response.to_dict()

def sync_accounts(access_token_encrypted: str):
    access_token = decrypt(access_token_encrypted)
    log_plaid_call("accounts_get", f"token_hash={hash(access_token)}")
    response = plaid_client.accounts_get(AccountsGetRequest(access_token=access_token))
    return response.accounts

# Fetch new transactions for a BankItem
def fetch_new_transactions(access_token: str, cursor: str = None):
    if cursor:
        request = TransactionsSyncRequest(access_token=access_token, cursor=cursor)
    else:
        request = TransactionsSyncRequest(access_token=access_token)

    response = plaid_client.transactions_sync(request)

    all_added = response['added']
    next_cursor = response['next_cursor']

    while response['has_more']:
        request = TransactionsSyncRequest(access_token=access_token, cursor=next_cursor)
        response = plaid_client.transactions_sync(request)
        all_added += response['added']
        next_cursor = response['next_cursor']

    log_plaid_call("transactions_sync COMPLETE", f"added={len(all_added)}")

    # TEST Debug print
    for txn in all_added:
        print(f"[INFO] Plaid sent txn: {txn['name']} | ${txn['amount']} on {txn['date']}")

    return all_added, next_cursor

# Save transactions to db
def save_transactions_to_db(transactions, user_id, bank_item_id, db):
    for txn in transactions:
        exists = db.query(Transaction).filter_by(plaid_transaction_id=txn["transaction_id"]).first()
        if exists:
            continue

        account = db.query(Account).filter_by(plaid_account_id=txn['account_id']).first()
        if not account:
            continue  # skip if account isn't found

        new_txn = Transaction(
            plaid_transaction_id = txn['transaction_id'],
            account_id = account.id,
            plaid_account_id = txn['account_id'],
            user_id = user_id,
            bank_item_id = bank_item_id,
            merchant_name = txn.get('merchant_name'),
            name = txn['name'],
            amount = txn['amount'],
            payment_channel = txn.get('payment_channel'),
            iso_currency_code = txn.get('iso_currency_code'),
            personal_finance_category_primary = txn.get("personal_finance_category", {}).get("primary"),
            personal_finance_category_detailed = txn.get("personal_finance_category", {}).get("detailed"),
            date = txn['date'],
            authorized_date = txn.get('authorized_date'),
            pending = txn['pending']
        )
        db.add(new_txn)

# Fetch and save new transactions for a BankItem
def sync_transactions_for_item(bank_item, user_id):
    db = sessionlocal()
    access_token = decrypt(bank_item.access_token_encrypted)
    transactions, new_cursor = fetch_new_transactions(access_token, bank_item.cursor)
    # TEST Debug print
    if not transactions:
        print(f"[INFO] No new transactions for item {bank_item.id}")
        return
    save_transactions_to_db(transactions, user_id, bank_item.id, db)
    bank_item.cursor = new_cursor
    db.commit()
    db.close()

# Fetch and save new transactions for all BankItem
def sync_all_transactions(user_id: int = 1): # hardcoded for now
    db = sessionlocal()
    items = db.query(BankItem).filter_by(user_id=user_id).all()
    for item in items:
        sync_transactions_for_item(item, user_id)
    db.close()

def get_dashboard_data(user_id: int = 1): # hardcoded for now
    db = sessionlocal()

    # Linked accounts
    db_linked_accounts = db.query(Account).filter_by(user_id=user_id).all()
    linked_accounts = [
        {
            "id": account.id,
            "name": db.query(BankItem).filter_by(id=account.bank_item_id).first().institution_name,
            "lastFour": account.mask,
            "accountType": account.subtype
        }
        for account in db_linked_accounts
    ]

    # Transactions

    # Only data from current month
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)
    if now.month == 12:
        start_of_next_month = datetime(now.year + 1, 1, 1)
    else:
        start_of_next_month = datetime(now.year, now.month + 1, 1)

    db_transactions = (
        db.query(Transaction)
        .filter_by(user_id=user_id)
        .filter(Transaction.amount > 0)  # Filter for expenses
        .filter(
            and_(
                Transaction.date >= start_of_month,
                Transaction.date < start_of_next_month
            )
        )
        .order_by(Transaction.date.desc())
        .all()
    )

    transactions = [
        {
            "id": t.id,
            "date": t.date.strftime("%Y-%m-%d"),
            "merchant": t.merchant_name,
            "original_name": t.name,
            "category": t.personal_finance_category_primary,
            "amount": t.amount
        }
        for t in db_transactions
    ]

    # Spent by category
    spend_by_category = defaultdict(float)
    for t in transactions:
        print("The whole list:", t)
        if t["amount"] > 0: # only expenses
            spend_by_category[t["category"]] += float(abs(t["amount"]))

    categories = db.query(DefaultCategory).all()
    category_map = {c.name: c.color for c in categories}

    spending_by_category = [
        {
            "name": cat,
            "value": round(spend, 2),
            "color": category_map.get(cat, "#6b7280")
        }
        for cat, spend in spend_by_category.items()
    ]
    db.close()

    # Total spent
    total_spent = 0

    for t in transactions:
        if t["amount"] > 0:
            total_spent += t["amount"]

    total_spent = abs(round(total_spent, 2))

    return {
        "total_spent": total_spent,
        "linked_banks": linked_accounts,
        "transactions": transactions,
        "spending_by_category": spending_by_category,
    }

def get_transactions_data(user_id: int = 1): # hardcoded for now
    db = sessionlocal()

    # Categories
    db_all_categories = db.query(DefaultCategory).all() # should also retrieve info from custom categories
    # continue working here
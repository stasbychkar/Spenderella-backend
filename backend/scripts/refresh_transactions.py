import os
from plaid.model.transactions_refresh_request import TransactionsRefreshRequest
from backend.utils.plaid_utils import plaid_client
from backend.db import sessionlocal
from backend.utils.crypto import decrypt
from backend.models import BankItem
from dotenv import load_dotenv

load_dotenv()

def refresh_fake_transactions():
    db = sessionlocal()

    # Get the access_token from your first linked bank item
    item = db.query(BankItem).filter_by(user_id=1).first()
    if not item:
        print("No bank item found.")
        return

    access_token = decrypt(item.access_token_encrypted)

    print("Requesting fake transactions refresh from Plaid...")
    request = TransactionsRefreshRequest(access_token=access_token)
    plaid_client.transactions_refresh(request)

    print("Refresh request sent. Now run /sync-all-transactions to fetch them.")
    db.close()

if __name__ == "__main__":
    refresh_fake_transactions()
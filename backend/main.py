from fastapi import FastAPI
from backend.utils.plaid_utils import create_link_token, exchange_public_token, sync_all_transactions, sync_transactions_for_item
from backend.services.bank_item_service import save_bank_item
from backend.services.accounts_service import save_accounts
from backend.schemas.plaid_schemas import TokenModel, AccessModel, SyncRequestModel
from backend.utils.plaid_utils import sync_accounts
# import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from backend.db import sessionlocal
from backend.models import BankItem
from backend.utils.crypto import encrypt, decrypt
from backend.routers.webhook_router import webhook_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use "*" during dev. Later restrict to frontend origin.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register webhook router
app.include_router(webhook_router)

@app.get("/link-token")
def get_link_token():
    return create_link_token()

@app.post("/exchange-token")
def exchange_token(body: TokenModel):
    plaid_response = exchange_public_token(body.public_token)

    access_token = plaid_response["access_token"]
    access_token_encrypted = encrypt(access_token)
    plaid_item_id = plaid_response["item_id"]
    institution_name = body.institution_name
    user_id = 1 # hardcoded

    webhook_url = "https://fa07-2601-600-9380-ca0-4dc5-8b48-1a4e-4b57.ngrok-free.app/webhook"

    new_item = save_bank_item(
        user_id=user_id,
        plaid_item_id=plaid_item_id,
        access_token_encrypted=access_token_encrypted,
        institution_name=institution_name,
        webhook_url=webhook_url
    )

    # Sync and save accounts
    accounts = sync_accounts(access_token_encrypted)
    save_accounts(accounts, plaid_item_id, user_id)

    # Sync and save transactions
    sync_transactions_for_item(new_item, user_id)

    return {
        "message": "Bank item saved",
        "item_id": plaid_item_id,
    }

@app.post('/sync-all-transactions')
def sync_all():
    sync_all_transactions()
    return {"message": "Synced all transactions"}
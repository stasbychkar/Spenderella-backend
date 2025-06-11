from fastapi import FastAPI
from backend.utils.plaid_utils import create_link_token, exchange_public_token, get_transactions
from backend.services.bank_item_service import save_bank_item
from backend.schemas.plaid_schemas import TokenModel, AccessModel, SyncRequestModel
# import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from backend.db import sessionlocal
from backend.models import BankItem
from backend.utils.crypto import encrypt, decrypt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use "*" during dev. Later restrict to frontend origin.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/link-token")
def get_link_token():
    return create_link_token()

@app.post("/exchange-token")
def exchange_token(body: TokenModel):
    plaid_response = exchange_public_token(body.public_token)

    access_token = plaid_response["access_token"]
    access_token_encrypted = encrypt(access_token)
    item_id = plaid_response["item_id"]
    institution_name = body.institution_name

    new_item = save_bank_item(
        user_id=1,
        item_id=item_id,
        access_token_encrypted=access_token_encrypted,
        institution_name=institution_name
    )

    return {
        "message": "Bank item saved",
        "item_id": item_id,
        "access_token": access_token_encrypted,
    }


@app.post("/transactions")
def transactions(body: AccessModel):
    access_token = decrypt(body.access_token)
    return get_transactions(access_token)

# @app.get("/sync-transactions")
# def sync(sync_request: SyncRequestModel):
#     result = sync_transactions(sync_request.item_id)
#     return result

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
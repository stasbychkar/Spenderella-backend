from fastapi import FastAPI
from backend.plaid_utils import create_link_token, exchange_public_token, get_transactions
# import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

class TokenModel(BaseModel):
    public_token: str
    institution_name: str

class AccessModel(BaseModel):
    access_token: str

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

    db = sessionlocal()
    new_item = BankItem(
        user_id=1,
        item_id=item_id,
        access_token=access_token_encrypted,
        institution_name=institution_name
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    db.close()

    return {
        "message": "Bank item saved",
        "item_id": item_id,
        "access_token": access_token_encrypted,
    }


@app.post("/transactions")
def transactions(body: AccessModel):
    access_token = decrypt(body.access_token)
    return get_transactions(access_token)

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
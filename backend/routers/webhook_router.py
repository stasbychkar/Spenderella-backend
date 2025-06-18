from fastapi import APIRouter, Request
from backend.utils.plaid_utils import sync_transactions
from backend.models import BankItem
from backend.db import sessionlocal

webhook_router = APIRouter()

webhook_router.post("/webhook")
async def plaid_webhook(request: Request):
    body = await request.json()
    print("Webhook received:", body)

    # Check if it's the type we need
    if (
        body.get("webhook_type") == "TRANSACTIONS"
        and body.get("webhook_code") == "SYNC_UPDATES_AVAILABLE"
    ):
        item_id = body.get("item_id")
        db = sessionlocal()
        item = db.query(BankItem).filter_by(plaid_item_id=item_id).first()
        if item:
            access_token = item.access_token_encrypted
            print(f"🔄 Syncing transactions for item_id: {item_id}")
            sync_transactions(access_token=item.access_token_encrypted)
        db.close()

    return {"status": "ok"}
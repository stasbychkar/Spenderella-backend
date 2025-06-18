from fastapi import APIRouter, Request
from backend.db import sessionlocal
from backend.models import BankItem
from backend.utils.crypto import decrypt
from backend.utils.plaid_utils import sync_transactions_for_item

webhook_router = APIRouter()

@webhook_router.post("/webhook")
async def plaid_webhook(request: Request):
    body = await request.json()
    print("Webhook received:", body)

    # Check if it's needed type
    if (
        body.get("webhook_type") == "TRANSACTIONS"
        and body.get("webhook_code") == "SYNC_UPDATES_AVAILABLE"
    ):
        item_id = body.get("item_id")
        db = sessionlocal()
        item = db.query(BankItem).filter_by(plaid_item_id=item_id).first()

        if item:
            print(f"Syncing transactions for item_id: {item_id}")
            sync_transactions_for_item(item, item.user_id, db)

        db.close()

    return {"status": "ok"}
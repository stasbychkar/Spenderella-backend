from backend.utils.plaid_utils import plaid_client
from backend.models import BankItem
from backend.db import sessionlocal
from backend.utils.crypto import decrypt
from plaid.model.sandbox_item_fire_webhook_request import SandboxItemFireWebhookRequest

db = sessionlocal()
item = db.query(BankItem).first()
access_token = decrypt(item.access_token_encrypted)

request = SandboxItemFireWebhookRequest(
    access_token=access_token,
    webhook_code="SYNC_UPDATES_AVAILABLE"
)

plaid_client.sandbox_item_fire_webhook(request)
print("Webhook fired for sandbox item")
db.close()

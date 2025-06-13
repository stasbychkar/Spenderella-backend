from backend.db import sessionlocal
from backend.models import BankItem

def save_bank_item(user_id: int, plaid_item_id: str, access_token_encrypted: str, institution_name: str):
    db = sessionlocal()
    new_item = BankItem(
        user_id=1,
        plaid_item_id=plaid_item_id,
        access_token_encrypted=access_token_encrypted,
        institution_name=institution_name
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    db.close()
    return new_item

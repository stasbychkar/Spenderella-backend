from backend.db import sessionlocal
from backend.models import Account, BankItem

def save_accounts(accounts, plaid_item_id, user_id):
    db = sessionlocal()

    bank_item = db.query(BankItem).filter_by(plaid_item_id=plaid_item_id).first()
    bank_item_id = bank_item.id

    for account in accounts:
        plaid_account_id = account.account_id

        new_account = Account(
            plaid_account_id=plaid_account_id,
            bank_item_id=bank_item_id,
            user_id=user_id,

            name=account.name,
            official_name=account.official_name,
            type = str(account.type),
            subtype = str(account.subtype),
            mask = account.mask,
        )

        db.add(new_account)

    db.commit()
    db.close()
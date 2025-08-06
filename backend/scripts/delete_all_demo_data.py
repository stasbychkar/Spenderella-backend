from sqlalchemy.orm import Session
from backend.db import engine
from backend.models import User, BankItem, Account, Transaction, DefaultCategory, CustomCategory

with Session(engine) as session:
    session.query(Account).filter(Account.plaid_account_id == None).delete(synchronize_session=False)
    session.query(User).filter(User.is_demo == True).delete(synchronize_session=False)

    session.commit()
    print("All demo data deleted successfully")


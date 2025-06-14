from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Boolean
from backend.db import Base
from sqlalchemy.orm import relationship

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    plaid_transaction_id = Column(String, unique=True) # transaction_id

    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"))
    plaid_account_id = Column(String)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    bank_item_id = Column(Integer, ForeignKey("bank_items.id", ondelete="CASCADE"))

    merchant_name = Column(String) # cleaned up name
    name = Column(String) # raw name
    amount = Column(Numeric)
    payment_channel = Column(String)
    iso_currency_code = Column(String(3))
    personal_finance_category_primary = Column(String)
    personal_finance_category_detailed = Column(String)
    date = Column(Date) # credit cards | when transaction is posted (later)
    authorized_date = Column(Date) # credit cards | when transaction happened (earlier)
    pending = Column(Boolean)

    account = relationship("Account", backref="transactions", passive_deletes=True)
    user = relationship("User", backref="transactions")
    bank_item = relationship("BankItem", backref="transactions", passive_deletes=True)
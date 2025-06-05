from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from backend.db import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    bank_item_id = Column(Integer, ForeignKey("bank_items.id"))
    account_id = Column(String) # from Plaid
    name = Column(String)
    type = Column(String)
    subtype = Column(String)
    balance = Column(Numeric)
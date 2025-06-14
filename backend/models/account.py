from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from backend.db import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    plaid_account_id = Column(String, unique=True)

    bank_item_id = Column(Integer, ForeignKey("bank_items.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id"))

    name = Column(String)
    official_name = Column(String)
    type = Column(String)
    subtype = Column(String)
    mask = Column(String(4)) # last 4 digits

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bank_item = relationship("BankItem", backref="accounts", passive_deletes=True)
    user = relationship("User", backref="accounts")

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from backend.db import Base
from datetime import datetime

class BankItem(Base):
    __tablename__ = "bank_items"

    id = Column(Integer, primary_key=True)
    plaid_item_id = Column(String) # from Plaid
    user_id = Column(Integer, ForeignKey("users.id"))
    
    access_token_encrypted = Column(String)
    institution_name = Column(String)
    institution_logo = Column(String) # from Plaid, separate API call
    plaid_institution_id = Column(String) # from Plaid

    cursor = Column(String, nullable=True)
    webhook_url = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
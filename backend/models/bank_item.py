from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from backend.db import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class BankItem(Base):
    __tablename__ = "bank_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    plaid_item_id = Column(String) # from Plaid
    plaid_institution_id = Column(String) # from Plaid
    
    access_token_encrypted = Column(String)
    institution_name = Column(String)
    institution_logo = Column(String) # from Plaid, separate API call

    cursor = Column(String, nullable=True)
    webhook_url = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship(
        "User",
        backref="bank_items",
        passive_deletes=True
    )
from sqlalchemy import Column, Integer, String, ForeignKey
from backend.db import Base

class BankItem(Base):
    __tablename__ = "bank_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(String) # from Plaid
    access_token = Column(String) # will encrypt this
    institution_name = Column(String)
    cursor = Column(String, nullable=True)
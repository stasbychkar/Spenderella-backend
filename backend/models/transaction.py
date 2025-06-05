from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Boolean
from backend.db import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    amount = Column(Numeric)
    category = Column(String)
    date = Column(Date)
    pending = Column(Boolean)
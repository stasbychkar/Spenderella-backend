from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.db import Base
from datetime import datetime

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    problem = Column(String)
    openToCall = Column(Boolean)
    time = Column(DateTime, default=datetime.utcnow)
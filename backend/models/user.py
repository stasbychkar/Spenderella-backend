from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from backend.db import Base
from sqlalchemy.orm import relationship

# MVP: single-user app

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    custom_categories = relationship("CustomCategory", backref="user", passive_deletes=True)
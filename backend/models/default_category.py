from sqlalchemy import Column, Integer, String
from backend.db import Base

class DefaultCategory(Base):
    __tablename__ = "default_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    color = Column(String)
    
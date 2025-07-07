from sqlalchemy import Column, Integer, String
from backend.db import Base

class GeneralCategory(Base):
    __tablename__ = "general_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    color = Column(String)
    
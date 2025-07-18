from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from backend.db import Base

class CustomCategory(Base):
    __tablename__ = "custom_categories"

    id = Column(Integer, Sequence('my_model_id_seq', start=100), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String)
    color = Column(String)
    
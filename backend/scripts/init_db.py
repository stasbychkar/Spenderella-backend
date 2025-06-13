# creates database schema
from backend.db import Base, engine
from backend.models import User, BankItem, Account, Transaction

# Drop all tabels
Base.metadata.drop_all(bind=engine)

# Create tables based on existing models
Base.metadata.create_all(bind=engine)   
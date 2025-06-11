# creates database schema
from backend.db import Base, engine
from backend.models import User, BankItem, Account, Transaction

Base.metadata.create_all(bind=engine)   
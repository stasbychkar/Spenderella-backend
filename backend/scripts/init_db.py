# creates database schema
from backend.db import Base, engine
from backend.models import User, BankItem, Account, Transaction, DefaultCategory, CustomCategory

# # Drop all tabels
# Base.metadata.drop_all(bind=engine)

# Drop only [...]
# for table in [Transaction.__table__, Account.__table__, BankItem.__table__, CustomCategory.__table__]:
#     table.drop(bind=engine, checkfirst=True)

# for table in [DefaultCategory.__table__]:
#     table.drop(bind=engine, checkfirst=True)

Base.metadata.drop_all(engine)

# Create tables based on existing models
Base.metadata.create_all(bind=engine)
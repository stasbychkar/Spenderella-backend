# backend/scripts/seed_general_categories.py

from sqlalchemy.orm import Session
from backend.db import engine
from backend.models import DefaultCategory

categories = [
    {"name": "INCOME", "color": "#10b981"},
    {"name": "TRANSFER_IN", "color": "#06b6d4"},
    {"name": "TRANSFER_OUT", "color": "#0891b2"},
    {"name": "LOAN_PAYMENTS", "color": "#f97316"},
    {"name": "BANK_FEES", "color": "#ef4444"},
    {"name": "ENTERTAINMENT", "color": "#f59e0b"},
    {"name": "FOOD_AND_DRINK", "color": "#3b82f6"},
    {"name": "GENERAL_MERCHANDISE", "color": "#8b5cf6"},
    {"name": "HOME_IMPROVEMENT", "color": "#a855f7"},
    {"name": "MEDICAL", "color": "#e11d48"},
    {"name": "PERSONAL_CARE", "color": "#f472b6"},
    {"name": "GENERAL_SERVICES", "color": "#22c55e"},
    {"name": "GOVERNMENT_AND_NON_PROFIT", "color": "#7c3aed"},
    {"name": "TRANSPORTATION", "color": "#0ea5e9"},
    {"name": "TRAVEL", "color": "#14b8a6"},
    {"name": "RENT_AND_UTILITIES", "color": "#d97706"},
]

with Session(engine) as session:
    for cat in categories:
        exists = session.query(DefaultCategory).filter_by(name=cat["name"]).first()
        if not exists:
            session.add(DefaultCategory(name=cat["name"].replace('_', ' ').title(), color=cat["color"]))
    session.commit()
    print("Default categories seeded.")
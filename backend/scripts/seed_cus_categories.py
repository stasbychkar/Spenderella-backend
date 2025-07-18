# backend/scripts/seed_cus_categories.py

from sqlalchemy.orm import Session
from backend.db import engine
from backend.models import CustomCategory

categories = [
    {"name": "Custom1", "user_id": 1, "color": "#FF4136"},
    {"name": "Custom2", "user_id": 1, "color": "#2ECC40"},
    {"name": "Custom3", "user_id": 1, "color": "#7FDBFF"},
]

with Session(engine) as session:
    for cat in categories:
        exists = session.query(CustomCategory).filter_by(name=cat["name"]).first()
        if not exists:
            session.add(CustomCategory(name=cat["name"], user_id=cat["user_id"], color=cat["color"]))
    session.commit()
    print("Custom categories seeded.")
# scripts/make_admin.py
from app.app.database import SessionLocal
from app.app import models

# python -m app.app._scripts.admin

db = SessionLocal()

user = db.query(models.User).filter(models.User.login_id == "kanekodemo").first()
user.is_admin = True
db.commit()

print("admin化しました")

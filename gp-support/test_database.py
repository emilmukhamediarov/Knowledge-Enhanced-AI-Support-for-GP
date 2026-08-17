from sqlalchemy import select

from database import SessionLocal
from models import User


session = SessionLocal()

user = User(name="Alice")

session.add(user)
session.commit()

users = session.scalars(select(User)).all()

for user in users:
    print(user.id, user.name)

session.close()
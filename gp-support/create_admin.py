from app.db.database import SessionLocal
from app.db import models
from app.services.auth_service import get_password_hash

def seed_admin():
    db = SessionLocal()
    try:
        # 1. Check if the admin already exists to avoid duplicates
        admin_user = db.query(models.User).filter(models.User.username == "admin").first()

        if admin_user:
            print("Admin user already exists")
            return

        # 2. Create the new admin user
        new_admin = models.User(
            username="admin",
            name="Super Admin",
            hashed_password=get_password_hash("password123"),
            role="admin"
        )

        # 3. Save to database
        db.add(new_admin)
        db.commit()
        print("Successfully created admin user: 'admin'")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
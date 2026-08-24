import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
# from app.config import SECRET_KEY, ALGORITHM
from app.dependencies.db import get_db
from app.db import models

# --- Configuration ---
# In production, change this secret key and load it from an environment variable for now it's fine
SECRET_KEY = "my_super_secret_key_for_gp_support"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 999

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def RequireRole(required_roles: list[str]):
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in required_roles and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return role_checker
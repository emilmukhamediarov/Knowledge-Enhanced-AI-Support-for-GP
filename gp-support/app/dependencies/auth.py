import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db import models
from app.dependencies.db import get_db
from app.config import (
    AUTH_SECRET_KEY,
    AUTH_ALGORITHM,
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            AUTH_SECRET_KEY,
            algorithms=[AUTH_ALGORITHM]
        )

        username = payload.get("sub")

        if not username:
            raise credentials_exception

    except jwt.PyJWTError:
        raise credentials_exception

    user = (
        db.query(models.User)
        .filter(models.User.username == username)
        .first()
    )

    if user is None:
        raise credentials_exception

    return user


def require_role(
    required_roles: list[models.UserRole]
):
    def role_checker(
        current_user: models.User = Depends(get_current_user)
    ) -> models.User:

        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        return current_user

    return role_checker
import os, time
import bcrypt, jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from . import models

SECRET = os.getenv("SECRET_KEY", "dev")
bearer = HTTPBearer(auto_error=False)


def hash_pw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def verify_pw(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())


def make_token(user_id: int) -> str:
    return jwt.encode({"sub": str(user_id), "exp": int(time.time()) + 7 * 86400}, SECRET, "HS256")


def optional_user(cred: HTTPAuthorizationCredentials | None = Depends(bearer),
                  db: Session = Depends(get_db)) -> models.User | None:
    if not cred:
        return None
    try:
        uid = int(jwt.decode(cred.credentials, SECRET, ["HS256"])["sub"])
    except Exception:
        return None
    return db.get(models.User, uid)


def current_user(user: models.User | None = Depends(optional_user)) -> models.User:
    if not user:
        raise HTTPException(401, "Please sign in")
    return user

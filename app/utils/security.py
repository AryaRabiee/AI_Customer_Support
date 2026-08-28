from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from jose import jwt ,JWTError
from fastapi.security import HTTPAuthorizationCredentials
import os
password_hash = PasswordHash.recommended()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str,hashed_password: str) -> bool:
    
    return password_hash.verify(plain_password,hashed_password)


def create_access_token(user_id : int) ->str:

    expire = (datetime.now(timezone.utc) + timedelta(minutes=60))

    payload = {
        "sub":str(user_id),
        "type":"access",
        "exp":int(expire.timestamp())
    }

    token = jwt.encode(payload ,SECRET_KEY , algorithm=ALGORITHM )

    return token

def create_refresh_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=7
    )

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": int(expire.timestamp())
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "access":
            return None

        return payload

    except JWTError:
        return None

def decode_refresh_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "refresh":
            return None

        return payload

    except JWTError:
        return None
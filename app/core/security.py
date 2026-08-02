import hmac
import hashlib
import time
import datetime as dt
from jose import jwt
from fastapi import Request, Header, HTTPException
from app.config import settings


def compute_signature(raw_body: bytes, timestamp: str, secret: str) -> str:
    message = timestamp.encode() + b"." + raw_body
    signature = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    return signature

def verify_signature(raw_body: bytes, received_signature: str, timestamp: str, secret: str, tolerance_seconds: int = 300) -> tuple[bool, str]:
    try:
        request_time = int(timestamp)
    except ValueError:
        return False, "Invalid timestamp format"

    current_time = int(time.time())
    if abs(current_time - request_time) > tolerance_seconds:
        return False, "Timestamp outside tolerance window (possible replay attack)"

    expected_signature = compute_signature(raw_body, timestamp, secret)

    if not hmac.compare_digest(expected_signature, received_signature):
        return False, "Signature mismatch"

    return True, "Valid"

async def require_valid_signature(
    request: Request,
    x_signature: str = Header(...),
    x_timestamp: str = Header(...),
) -> bytes:
    raw_body = await request.body()

    is_valid, reason = verify_signature(
        raw_body=raw_body,
        received_signature=x_signature,
        timestamp=x_timestamp,
        secret=settings.WEBHOOK_SIGNING_SECRET,
    )

    if not is_valid:
        raise HTTPException(status_code=401, detail=f"Webhook signature verification failed: {reason}")

    return raw_body

def authenticate_client(client_id: str, client_secret: str) -> bool:
    return (
        client_id == settings.REGISTERED_CLIENT_ID
        and client_secret == settings.REGISTERED_CLIENT_SECRET
    )


def create_access_token(client_id: str) -> str:
    expire = dt.datetime.utcnow() + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": client_id,
        "exp": expire,
        "iat": dt.datetime.utcnow(),
    }

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token
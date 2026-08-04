import hmac
import hashlib
import time
import datetime as dt
from jose import jwt
from fastapi import Request, Header, HTTPException
from app.config import settings
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="oauth/token")

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
        hmac.compare_digest(client_id, settings.REGISTERED_CLIENT_ID)
        and hmac.compare_digest(client_secret, settings.REGISTERED_CLIENT_SECRET)
    )


def create_access_token(client_id: str, scopes: list[str]) -> str:
    expire = dt.datetime.utcnow() + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": client_id,
        "scopes": scopes,
        "exp": expire,
        "iat": dt.datetime.utcnow(),
    }

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def get_current_client(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    client_id = payload.get("sub")
    if not client_id:
        raise HTTPException(status_code=401, detail="Token missing subject claim")

    return client_id

class RequireScope:
    def __init__(self, required_scope: str):
        self.required_scope = required_scope

    def __call__(self, token: str = Depends(oauth2_scheme)) -> str:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        token_scopes = payload.get("scopes", [])
        if self.required_scope not in token_scopes:
            raise HTTPException(
                status_code=403,
                detail=f"Token missing required scope: {self.required_scope}",
            )

        return payload.get("sub")
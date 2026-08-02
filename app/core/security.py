import hmac
import hashlib
import time


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
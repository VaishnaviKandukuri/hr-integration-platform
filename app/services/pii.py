import re


def mask_email(email: str) -> str:
    local_part, domain = email.split("@")
    if len(local_part) <= 1:
        return f"{local_part}***@{domain}"
    return f"{local_part[0]}{'*' * (len(local_part) - 1)}@{domain}"

def mask_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 2:
        return "*" * len(digits)
    return ("*" * (len(digits) - 2)) + digits[-2:]


def last4_national_id(national_id: str) -> str:
    digits = re.sub(r"\W", "", national_id)
    return digits[-4:] if len(digits) >= 4 else digits
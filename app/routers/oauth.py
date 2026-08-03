from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import authenticate_client, create_access_token
from app.config import settings

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.post("/token")
def issue_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if not authenticate_client(form_data.username, form_data.password):
        raise HTTPException(status_code=401, detail="Invalid client credentials")

    access_token = create_access_token(form_data.username, settings.REGISTERED_CLIENT_SCOPES)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

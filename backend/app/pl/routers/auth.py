from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.bll.exceptions import (
    AuthenticationException,
    InvalidRoleException,
    UserNotFoundException,
)
from app.bll.services.auth_service import AuthService
from app.pl.dependencies import get_auth_service
from app.pl.schemas import MockLoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    try:
        return service.login(form_data.username, form_data.password)
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post("/mock-login", response_model=TokenResponse)
def mock_login(
    request: MockLoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return service.mock_login(request.role, request.profile_id)
    except InvalidRoleException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

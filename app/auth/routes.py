from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.database.database import User, get_db


# ============================================================
# ROUTER CONFIGURATION
# ============================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# SIGNUP REQUEST MODEL
# ============================================================

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


# ============================================================
# SIGNUP RESPONSE MODEL
# ============================================================

class SignupResponse(BaseModel):
    message: str
    user_id: int
    username: str


# ============================================================
# LOGIN REQUEST MODEL
# ============================================================

class LoginRequest(BaseModel):
    username: str
    password: str


# ============================================================
# LOGIN RESPONSE MODEL
# ============================================================

class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    user_id: int
    username: str


# ============================================================
# SIGNUP
# ============================================================

@router.post(
    "/signup",
    response_model=SignupResponse,
)
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new user account.
    """

    username = request.username.strip()
    email = request.email.strip().lower()
    password = request.password

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if len(username) < 3:
        raise HTTPException(
            status_code=400,
            detail="Username must contain at least 3 characters.",
        )

    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 8 characters.",
        )

    if "@" not in email or "." not in email:
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid email address.",
        )

    # --------------------------------------------------------
    # Check existing username
    # --------------------------------------------------------

    existing_username = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=409,
            detail="Username already exists.",
        )

    # --------------------------------------------------------
    # Check existing email
    # --------------------------------------------------------

    existing_email = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email already exists.",
        )

    # --------------------------------------------------------
    # Hash password
    # --------------------------------------------------------

    password_hash = hash_password(password)

    # --------------------------------------------------------
    # Create user
    # --------------------------------------------------------

    new_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return SignupResponse(
        message="Account created successfully.",
        user_id=new_user.id,
        username=new_user.username,
    )


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return a JWT access token.
    """

    username = request.username.strip()

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    # --------------------------------------------------------
    # Generic authentication error
    # --------------------------------------------------------

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    # --------------------------------------------------------
    # Check account status
    # --------------------------------------------------------

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive.",
        )

    # --------------------------------------------------------
    # Verify password
    # --------------------------------------------------------

    password_valid = verify_password(
        request.password,
        user.password_hash,
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    # --------------------------------------------------------
    # Create JWT
    # --------------------------------------------------------

    access_token = create_access_token(
        user.id
    )

    # --------------------------------------------------------
    # Return authentication response
    # --------------------------------------------------------

    return LoginResponse(
        message="Login successful.",
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
    )
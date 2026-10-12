
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserLogin, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    location = user.location.strip()

    if not location:
        raise HTTPException(
            status_code=422,
            detail="Location cannot be empty",
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password,
        location=location,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def login_user(
    user: UserLogin,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if (
        not existing_user
        or existing_user.password != user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    return {
        "message": "Login successful",
        "user_id": existing_user.id,
        "name": existing_user.name,
        "email": existing_user.email,
        "location": existing_user.location,
    }

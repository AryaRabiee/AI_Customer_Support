from fastapi import APIRouter , HTTPException , Depends , status
from app.db.database import get_db
from fastapi import Request
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest , SignupRequest
from sqlalchemy.exc import SQLAlchemyError
from app.db.models import User , Order , Ticket
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.security import verify_password , create_access_token , hash_password , create_refresh_token , decode_refresh_token
from fastapi import Response
from app.api.dependencies.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login")
def login(data : LoginRequest ,response : Response, db : Session = Depends(get_db)):
    try:
        user = (db.query(User).filter(User.email == data.email)).first()
    except SQLAlchemyError as e:    
        logger.exception("Database error during login %s" , e)
        db.rollback()
        raise HTTPException(status_code=500, detail="Database Error")

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail="Invalid credentials")
    if not verify_password(data.password , user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail = "Invalid credentials")
    access_token = create_access_token(user.user_id)
    refresh_token = create_refresh_token(user.user_id)


    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    return {
        "message": "Login successful"
    }


@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="این ایمیل قبلاً ثبت شده است"
            )
        
        hashed_password = hash_password(data.password)
        new_user = User(
            email=data.email,
            name=data.name,
            password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "message": "ثبت نام موفق",
            "user_id": new_user.user_id
        }
        
    except SQLAlchemyError as e:
        logger.exception("Database error during signup %s" ,e)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطا در پایگاه داده"
        )

@router.get("/me")     
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "name": current_user.name,
        "email": current_user.email
    }

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {
        "message": "Logged out"
    }

@router.post("/refresh")
def refresh_token(
    request: Request,
    response: Response
):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )

    payload = decode_refresh_token(refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = int(payload["sub"])

    new_access_token = create_access_token(user_id)

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60
    )

    return {
        "message": "Access token refreshed"
    }
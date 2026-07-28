from fastapi import APIRouter , HTTPException , Depends , status
from db.database import get_db
from sqlalchemy.orm import Session
from schemas.auth import LoginRequest , SignupRequest
from sqlalchemy.exc import SQLAlchemyError
from db.models import User , Order , Ticket
from fastapi.security import OAuth2PasswordRequestForm
from utils.security import verify_password , create_access_token , hash_password
from fastapi import Response
from api.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login")
def login(data : LoginRequest ,response : Response, db : Session = Depends(get_db)):
    try:
        user = (db.query(User).filter(User.email == data.email)).first()
    except SQLAlchemyError as e:    
        print(f" ERROR: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database Error")

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail="Invalid credentials")
    if not verify_password(data.password , user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail = "Invalid credentials")
    access_token = create_access_token(user.user_id)


    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=30 * 60
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
        print(f"ERROR: {e}")
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
    return {"message": "Logged out"}
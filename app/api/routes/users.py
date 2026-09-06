from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_user
from app.db.models import User


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):

    return {
        "user_id": current_user.user_id,
        "name": current_user.name,
        "email": current_user.email
    }
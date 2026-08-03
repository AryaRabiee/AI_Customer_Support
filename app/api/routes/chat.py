from schemas.chat import ChatMessage
from fastapi import APIRouter ,status , HTTPException , Depends
from api.dependencies.auth import get_current_user
from graph.support_graph import run_support_agent
from db.models import User


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)
@router.post("/message")
async def chat_message( data: ChatMessage,current_user:User = Depends(get_current_user)):
    
    user_message = data.message.strip()
    print(user_message)
    if not user_message:   
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="پیام خالی است"
        )
    response = run_support_agent(user_message , current_user.user_id)
    return {    
        "response": response,
        "status": "success"
    }
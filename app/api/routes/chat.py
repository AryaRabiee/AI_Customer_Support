from schemas.chat import ChatMessage
from fastapi import APIRouter ,status , HTTPException , Depends
from api.dependencies.auth import get_current_user
from graph.support_graph import run_support_agent
from db.models import User
from exceptions.llm import LLMError , LLMTimeoutError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)
@router.post("/message")
async def chat_message( data: ChatMessage,current_user:User = Depends(get_current_user)):
    thread_id = current_user.user_id
    user_message = data.message.strip()
    logger.info(
    "Chat request received | user_id=%s | thread_id=%s",
    current_user.user_id,
    thread_id
)
    if not user_message:   
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="پیام خالی است"
        )
    try:
        response = run_support_agent(user_message , current_user.user_id,thread_id)

        return {    
            "response": response,
            "status": "success"
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
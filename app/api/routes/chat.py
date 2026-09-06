from app.schemas.chat import ChatMessage
from fastapi import APIRouter ,status , HTTPException , Depends
from fastapi.requests import Request
from fastapi.responses import StreamingResponse
from app.api.dependencies.auth import get_current_user
from app.graph.support_graph import run_support_agent , app
from app.db.models import User
from app.exceptions.llm import LLMError , LLMTimeoutError
import logging
import json
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)
def get_user_rate_key(request: Request):
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    return get_remote_address(request)
limiter = Limiter(key_func=get_user_rate_key)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post("/message")
@limiter.limit("14/minute")
async def chat_message(request :Request , data: ChatMessage,current_user:User = Depends(get_current_user)):
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

    except Exception as e:
        logger.exception("ERROR FROM CHAT_MESSAGES FUNC %s",e )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/history")
async def chat_history(
    current_user: User = Depends(get_current_user)
):
    thread_id = current_user.user_id

    try:
        state = app.get_state({
            "configurable": {"thread_id": thread_id}
        })
        
        if not state or not state.values:
            return {"messages": []}
        
        messages = state.values.get("messages", [])
        
        return {
            "messages": [
                {
                    "role": message.type,
                    "content": message.content
                }
                for message in messages
                if message.type in ("human", "ai")
            ]
        }
    except Exception as e:
        logger.error(f"Error loading chat history: {e}")
        return {"messages": []}  # خالی بجای خطا
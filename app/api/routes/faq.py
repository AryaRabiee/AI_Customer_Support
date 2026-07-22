from fastapi import APIRouter , HTTPException
from app.schemas.faq import FAGRequest , FAQResponse
from services.llm.fag_agent import rag_agent
from fastapi.responses import StreamingResponse
import json

router = APIRouter(
    prefix="/faq",
    tags=["FAG"]
)
@router.post("" , response_model=FAQResponse)
async def answer_user_question(request: FAGRequest):

    async def generate():

        try:
            for chunk in rag_agent(request.user_message):

                if chunk:
                    yield json.dumps(
                        {"chunk": chunk},
                        ensure_ascii=False
                    ) + "\n"

        except Exception as e:
            yield json.dumps(
                {"error": str(e)},
                ensure_ascii=False
            ) + "\n"

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson"
    )

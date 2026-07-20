from fastapi import APIRouter , HTTPException
from schemas.fag import FAGRequest , FAQResponse

router = APIRouter(
    prefix="/faq",
    tags=["FAG"]
)
@router.post("" , response_model=FAQResponse)
async def answer_user_question(request : FAGRequest ,) -> FAQResponse:

    return FAQResponse(
        answer=f"soal daryaft shod {request.user_message}"
    )

from typing import Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field 

class SupportState(TypedDict):
    user_message: str
    next_agent: Literal["chat", "rag", "database"]
    response: str

    intent: str | None
    order_id: int | None

class SupervisorDecision(BaseModel):
    next_agent: Literal["chat", "rag", "database"] = Field(
        description="The agent that should handle the request"
    )

class ExtractData(BaseModel):
    intent : Literal["order_status" , "order_details","cancel_order","return_order"]
    order_id: int | None = None

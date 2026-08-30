from typing import Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field 
from langgraph.graph import MessagesState

class SupportState(MessagesState):
    user_id: int | None
    user_message: str
    next_agent: Literal["chat", "rag", "database", "refund"]
    response: str

    intent: Literal[
        "order_status",
        "order_details",
        "refund_order",
        "return_order"
    ] | None

    order_id: int | None
    product_id: int | None

    refund_action: Literal[
        "ASK_REASON",
        "ASK_INFORMATION",
        "CHECK_DATABASE",
        "FINAL"
    ] | None

    reason: Literal[
        "wrong_product",
        "damaged_product",
        "technical_problem",
        "changed_mind",
        "not_as_described",
        "other"
    ] | None

    description: str | None

    decision: Literal[
        "APPROVE",
        "REJECT",
        "REVIEW"
    ] | None
class SupervisorDecision(BaseModel):
    next_agent: Literal["chat", "rag", "database"] = Field(
        description="The agent that should handle the request"
    )

class ExtractData(BaseModel):
    intent : Literal["order_status" , "order_details","return_order"]
    order_id: int | None = None

class RefundOutput(BaseModel):
    action: Literal[
        "ASK_REASON",
        "ASK_INFORMATION",
        "CHECK_DATABASE",
        "FINAL"
    ]

    reason: Literal[
        "wrong_product",
        "damaged_product",
        "technical_problem",
        "changed_mind",
        "not_as_described",
        "other"
    ] | None = None

    order_id: int | None = None
    product_id: int | None = None
    expected_product: str | None = None  
    received_product: str | None = None 
    description: str | None = None
    message: str


    
from pydantic import BaseModel , Field

class FAGRequest(BaseModel):
    user_message :str = Field(... , min_length=1 , max_length=1000 , description="User's customer support question")


class FAQResponse(BaseModel):
    answer : str
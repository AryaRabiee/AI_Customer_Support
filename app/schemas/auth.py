from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):

    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
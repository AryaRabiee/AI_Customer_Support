from fastapi import FastAPI
from app.api.routes.faq import router as fag_router
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.chat import router as chat_router
from fastapi.requests import Request
from jose import jwt
from app.utils.security import decode_access_token
from app.api.routes.chat import limiter
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.utils.logger import logging
from slowapi import Limiter  , _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

logger = logging.getLogger(__name__) 
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
file_path = Path(__file__).parent.parent

app = FastAPI(
    title="AI Customer Support Agent",
    version="0.1.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded , _rate_limit_exceeded_handler)
@app.middleware("http")
async def set_user_in_state(request: Request, call_next):
    token = request.cookies.get("access_token")
    if token:
        try:
            payload = decode_access_token(token)
            request.state.user_id = payload.get("sub")
        except Exception as e:
            logger.exception("ERROR AT MIDDELWARE FUNC" ,e)
            raise
    
    response = await call_next(request)
    return response
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    fag_router,
    prefix="/api/v1"
)
app.include_router(
    auth_router,
    prefix = "/api"
)
app.include_router(
    users_router,
    prefix = "/api"
)
app.include_router(
    chat_router,
    prefix="/api"
)

@app.get("/health")
async def health_check():
    return {
        "status": "ok"
    }

@app.get("/")
async def home():
    return FileResponse(file_path/"templates/home.html")

@app.get("/login")
async def login_page():
    return FileResponse(file_path/"templates/login.html")

@app.get("/support")
async def support_page():
    return FileResponse(file_path/"templates/support.html")
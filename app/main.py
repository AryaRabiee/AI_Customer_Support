from fastapi import FastAPI
from api.routes.faq import router as fag_router
from api.routes.auth import router as auth_router
from api.routes.users import router as users_router
from api.routes.chat import router as chat_router
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import utils.logger
file_path = Path(__file__).parent.parent

load_dotenv()
app = FastAPI(
    title="AI Customer Support Agent",
    version="0.1.0",
)

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

@app.get("/faq")
async def faq_page():
    return FileResponse(file_path/"templates/faq.html")


@app.get("/test")
async def test_page():
    return FileResponse(file_path/"templates/test_home.html")

@app.get("/login")
async def login_page():
    return FileResponse(file_path/"templates/login.html")

@app.get("/support")
async def support_page():
    return FileResponse(file_path/"templates/support.html")
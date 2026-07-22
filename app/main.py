from fastapi import FastAPI
from app.api.routes.faq import router as fag_router
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

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

@app.get("/health")
async def health_check():
    return {
        "status": "ok"
    }

@app.get("/")
async def root():
    return FileResponse(file_path/"templates/home.html")

@app.get("/fag")
async def support_page():
    return FileResponse(file_path/"templates/faq.html")


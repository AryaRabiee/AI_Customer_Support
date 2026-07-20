from fastapi import FastAPI
from api.routes.fag import router as fag_router
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(
    title="AI Customer Support Agent",
    version="0.1.0",
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



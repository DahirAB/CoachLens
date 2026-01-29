from fastapi import FastAPI
from .api.endpoints import router as api_router

app = FastAPI(title="CoachLens API")

app.include_router(api_router)

@app.get("/")
def health_check():
    return {"status": "CoachLens backend running"}

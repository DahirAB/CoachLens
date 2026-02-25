from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.endpoints import router as api_router
from .api.profile import router as profile_router
from .api.plans import router as plans_router

app = FastAPI(title="CoachLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(profile_router)
app.include_router(plans_router)


@app.get("/")
def health_check():
    return {"status": "CoachLens backend running"}

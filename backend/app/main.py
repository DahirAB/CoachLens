from fastapi import FastAPI

app = FastAPI(title="CoachLens API")

@app.get("/")
def health_check():
    return {"status": "CoachLens backend running"}

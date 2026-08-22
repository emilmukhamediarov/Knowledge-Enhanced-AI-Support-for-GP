from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from app.db import models
from app.routers import auth, users, consultations
from app.dependencies.auth import get_current_user
app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(consultations.router)

# frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "GP Support API is running"}

@app.get("/test-auth")
def test_auth(current_user: models.User = Depends(get_current_user)):
    return {"message": f"Success! You are authenticated as {current_user.username} {current_user.role}"}
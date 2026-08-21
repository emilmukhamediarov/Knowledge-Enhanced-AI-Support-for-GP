from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routers import users, consultations

app = FastAPI()

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

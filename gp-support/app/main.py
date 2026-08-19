from fastapi import FastAPI

from app.routers import auth, users, consultations

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(consultations.router)


@app.get("/")
def home():
    return {"message": "GP Support API is running"}

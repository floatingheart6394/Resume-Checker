# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.resumeRoutes import router as resume_router   # existing
from backend.auth import router as auth_router
from backend.database import engine
from backend import models

app = FastAPI(title="Resume Checker API")

# Create DB tables
models.Base = models  # no-op placeholder if not used
models.Base = None    # keep previous code intact (we will create tables like below)
# Create all tables
from backend.database import Base, engine
from backend import models as m
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(resume_router)

@app.get("/")
def home():
    return {"message": "Welcome to Resume Checker API"}

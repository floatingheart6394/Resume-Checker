from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.resumeRoutes import router as resume_router

app = FastAPI(title="Resume Checker API")

# 🔥 Allow frontend to call backend (CORS FIX)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins
    allow_credentials=True,
    allow_methods=["*"],   # POST, GET, OPTIONS etc.
    allow_headers=["*"],
)

# include routes
app.include_router(resume_router)

@app.get("/")
def home():
    return {"message": "Welcome to Resume Checker API"}

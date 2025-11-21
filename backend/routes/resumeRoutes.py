from fastapi import APIRouter, UploadFile, File, Form, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.services.aiService import get_resume_matches
from backend.auth import get_current_user
from backend.database import SessionLocal
from backend import models

router = APIRouter(prefix="/analyze", tags=["Analyze"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------
#  Analyze TEXT route
# ---------------------------
@router.post("/text")
async def analyze_text(
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Expects JSON:
    { "resume_text": "...", "job_description": "..." }
    """
    payload = await request.json()
    resume_text = payload.get("resume_text", "")
    job_description = payload.get("job_description", "")

    try:
        # Call your AI analysis function
        result = get_resume_matches(resume_text, job_description)

        # Save the result in DB (ResumeRecord)
        record = models.ResumeRecord(
            user_id=current_user.id,
            resume_text=resume_text,
            job_description=job_description,
            predicted_domain=result.get("predicted_domain"),
            match_score=str(result.get("overall_match")),
            matched_keywords=",".join(result.get("top_keywords", [])),
            missing_keywords=",".join(result.get("missing_keywords", [])),
            summary=result.get("summary", "")
        )

        db.add(record)
        db.commit()

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# ---------------------------
#  Analyze FILE route
# ---------------------------
@router.post("/file")
async def analyze_file(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handle PDF/DOCX/TXT upload
    """
    try:
        content = await file.read()

        # Convert file bytes -> text
        try:
            resume_text = content.decode("utf-8", errors="ignore")
        except Exception:
            resume_text = content.decode("latin-1", errors="ignore")

        # Call AI
        result = get_resume_matches(resume_text, job_description)

        # Save result in DB
        record = models.ResumeRecord(
            user_id=current_user.id,
            resume_text=resume_text,
            job_description=job_description,
            predicted_domain=result.get("predicted_domain"),
            match_score=str(result.get("overall_match")),
            matched_keywords=",".join(result.get("top_keywords", [])),
            missing_keywords=",".join(result.get("missing_keywords", [])),
            summary=result.get("summary", "")
        )

        db.add(record)
        db.commit()

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

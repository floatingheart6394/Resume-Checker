# backend/routes/resumeRoutes.py
from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from backend.services.aiService import get_resume_matches

# imports for file extraction area are already present in your version if you used them earlier
router = APIRouter()

@router.post("/analyze/text")
async def analyze_text(request: Request):
    """
    Expects JSON:
    { "resume_text": "...", "job_description": "..." }
    """
    payload = await request.json()
    resume_text = payload.get("resume_text", "")
    job_description = payload.get("job_description", "")
    try:
        result = get_resume_matches(resume_text, job_description)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/analyze/file")
async def analyze_file(file: UploadFile = File(...), job_description: str = Form(...)):
    try:
        content = await file.read()
        # call your extract_text_from_bytes helper if present; else decode
        try:
            resume_text = content.decode("utf-8", errors="ignore")
        except Exception:
            resume_text = content.decode("latin-1", errors="ignore")
        result = get_resume_matches(resume_text, job_description)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

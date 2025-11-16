from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from backend.services.aiService import get_resume_matches

# new imports for extraction
import io
import fitz                 # PyMuPDF
from docx import Document

router = APIRouter()


@router.post("/analyze/text")
async def analyze_text(resume_text: str = Form(...), job_description: str = Form(...)):
    try:
        match_result = get_resume_matches(resume_text, job_description)
        return JSONResponse(content={"result": match_result})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


def extract_text_from_bytes(content: bytes, filename: str = "") -> str:
    """
    Extract text from bytes content. Determine type from filename extension.
    Supports: .txt, .pdf, .docx
    """
    fname = filename.lower()
    # text file
    if fname.endswith(".txt") or (not fname and b"\0" not in content[:1000]):
        try:
            return content.decode("utf-8", errors="ignore")
        except Exception:
            try:
                return content.decode("latin-1", errors="ignore")
            except Exception:
                return ""

    # pdf
    if fname.endswith(".pdf") or content[:4] == b"%PDF":
        try:
            text = ""
            with fitz.open(stream=content, filetype="pdf") as pdf:
                for page in pdf:
                    text += page.get_text()
            return text
        except Exception:
            return ""

    # docx
    if fname.endswith(".docx") or b"PK" in content[:4]:
        try:
            bio = io.BytesIO(content)
            doc = Document(bio)
            paragraphs = [p.text for p in doc.paragraphs]
            return "\n".join(paragraphs)
        except Exception:
            return ""

    # fallback
    try:
        return content.decode("utf-8", errors="ignore")
    except Exception:
        return ""


@router.post("/analyze/file")
async def analyze_file(file: UploadFile = File(...), job_description: str = Form(...)):
    try:
        # read bytes
        content = await file.read()

        # extract text from bytes using helper
        resume_text = extract_text_from_bytes(content, filename=file.filename)

        # fallback if extraction failed
        if not resume_text.strip():
            return JSONResponse(content={"error": "Could not extract text from uploaded file."}, status_code=400)

        match_result = get_resume_matches(resume_text, job_description)
        return JSONResponse(content={"result": match_result})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

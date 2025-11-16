import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
AI_PATH = os.path.join(PROJECT_ROOT, "ai_service")
sys.path.append(AI_PATH)

from ai_service.model.recruiter_match import match_job_with_resumes

def get_resume_matches(resume_text: str, job_description: str):
    try:
        results = match_job_with_resumes(resume_text, job_description)
        if isinstance(results, list):
            return results[:10]
        return results
    except Exception as e:
        return {"error": str(e)}

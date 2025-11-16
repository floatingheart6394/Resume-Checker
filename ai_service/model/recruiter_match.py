import os
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Paths
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "resume_match.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "tfidf_vectorizer.pkl")
RESUME_FOLDER = os.path.join(os.path.dirname(BASE_DIR), "data", "sample_resumes")

# Load model & vectorizer
with open(MODEL_PATH, "rb") as f:
    model = joblib.load(f)
with open(VECTORIZER_PATH, "rb") as f:
    vectorizer = joblib.load(f)


def match_job_with_resumes(resume_text: str, job_description: str):
    """
    Compares an uploaded resume with sample resumes and job description using AI model.
    Returns similarity scores and predicted categories.
    """
    resumes_data = []

    # Add uploaded resume to the comparison list
    resumes_data.append({"file": "uploaded_resume.txt", "text": resume_text})

    # Also include existing sample resumes
    resume_files = [f for f in os.listdir(RESUME_FOLDER) if f.endswith(".txt")]
    for file in resume_files:
        path = os.path.join(RESUME_FOLDER, file)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        resumes_data.append({"file": file, "text": text})

    # Vectorize all texts (job + resumes)
    all_texts = [job_description] + [r["text"] for r in resumes_data]
    vectors = vectorizer.transform(all_texts)
    job_vec = vectors[0]
    resume_vecs = vectors[1:]

    # Calculate cosine similarity
    similarities = cosine_similarity(job_vec, resume_vecs)[0]

    # Predict categories
    preds = model.predict(resume_vecs)

    # Combine results
    results = sorted(
        [
            {
                "file": resumes_data[i]["file"],
                "similarity": round(float(similarities[i] * 100), 2),
                "predicted_domain": preds[i],
            }
            for i in range(len(resumes_data))
        ],
        key=lambda x: x["similarity"],
        reverse=True,
    )

    return results


if __name__ == "__main__":
    resume_text = input("📄 Paste your resume text: ")
    job_description = input("📝 Paste the job description: ")

    print("\n🔍 Matching resumes... Please wait...\n")
    matches = match_job_with_resumes(resume_text, job_description)

    print("\n📋 Top Matches:\n")
    for m in matches[:10]:
        print(f"{m['file']}  →  {m['similarity']}%  ({m['predicted_domain']})")

    print("\n🏁 Matching process complete.")

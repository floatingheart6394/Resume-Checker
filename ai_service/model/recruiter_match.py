import os
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import io
import base64

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

def _plot_bar_domain_scores(domain_scores):
    # domain_scores: list of (domain,score) sorted desc
    domains = [d for d, s in domain_scores]
    scores = [s for d, s in domain_scores]
    fig, ax = plt.subplots(figsize=(5, 2.5))
    y_pos = np.arange(len(domains))
    ax.barh(y_pos, scores, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(domains)
    ax.invert_yaxis()
    ax.set_xlabel("Match score")
    ax.set_title("Relevant domain matches")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def _plot_pie(overall_match):
    matched = overall_match
    remaining = max(0.0, 100.0 - matched)
    fig, ax = plt.subplots(figsize=(3.5,3.5))
    ax.pie([matched, remaining], labels=[f"Matched ({matched:.1f}%)", f"Remaining ({remaining:.1f}%)"],
           autopct=None, startangle=90)
    ax.set_title("Resume vs Job match")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def build_summary(overall_match, predicted_domain, top_keywords, missing_keywords):
    summary = (
        f"Your resume matches the job description by about {overall_match}%. "
        f"It appears most relevant to the {predicted_domain} domain. "
    )

    if top_keywords:
        summary += (
            f"Your resume contains strong keywords such as "
            f"{', '.join(top_keywords[:3])}. "
        )

    if missing_keywords:
        summary += (
            f"However, it is missing important terms such as "
            f"{', '.join(missing_keywords[:3])}. "
            "Adding these areas can improve your match."
        )

    return summary


def match_job_with_resumes(resume_text: str, job_description: str):
    """
    Returns:
      {
        overall_match: float (0-100),
        predicted_domain: str,
        top_keywords: [str,...],
        missing_keywords: [str,...],
        domain_scores: [(domain,score), ...]  # sorted desc
        bar_chart: base64_png,
        pie_chart: base64_png
      }
    """
    # Build list of sample resumes
    resumes_data = []
    resume_files = [f for f in os.listdir(RESUME_FOLDER) if f.endswith(".txt")]
    for file in resume_files:
        path = os.path.join(RESUME_FOLDER, file)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        resumes_data.append({"file": file, "text": text})

    # Add uploaded resume first
    all_texts = [job_description, resume_text] + [r["text"] for r in resumes_data]
    vectors = vectorizer.transform(all_texts)  # sparse
    job_vec = vectors[0]
    uploaded_vec = vectors[1]
    sample_vecs = vectors[2:]

    # overall similarity between job and uploaded resume
    overall_sim = cosine_similarity(job_vec, uploaded_vec)[0][0]  # scalar
    overall_match_pct = round(float(overall_sim * 100), 2)

    # Predict domain for uploaded resume using model
    try:
        pred_uploaded = model.predict(uploaded_vec)[0]
    except Exception:
        pred_uploaded = "Unknown"

    # Compute per-term contribution (job vs resume) using element-wise product
    # Get feature names
    try:
        feature_names = vectorizer.get_feature_names_out()
    except Exception:
        feature_names = None

    # elementwise product (sparse)
    prod = uploaded_vec.multiply(job_vec)  # sparse, shape (1, n_features)
    prod_arr = prod.toarray().ravel()  # dense 1D

    # pick top matched keywords: terms with highest product
    top_idx = np.argsort(prod_arr)[::-1]
    top_keywords = []
    if feature_names is not None:
        for idx in top_idx:
            if prod_arr[idx] <= 0:
                break
            top_keywords.append(feature_names[idx])
            if len(top_keywords) >= 7:
                break

    # If none matched, fall back to top job keywords
    if not top_keywords:
        job_arr = job_vec.toarray().ravel()
        job_idx = np.argsort(job_arr)[::-1]
        if feature_names is not None:
            for idx in job_idx[:7]:
                if job_arr[idx] <= 0:
                    continue
                top_keywords.append(feature_names[idx])

    # missing keywords: top job keywords that do not appear in resume (resume tfidf == 0)
    missing_keywords = []
    if feature_names is not None:
        job_arr = job_vec.toarray().ravel()
        job_top_idx = np.argsort(job_arr)[::-1]
        for idx in job_top_idx:
            if len(missing_keywords) >= 7:
                break
            if job_arr[idx] <= 0:
                break
            # resume tfidf
            if uploaded_vec.toarray().ravel()[idx] == 0:
                missing_keywords.append(feature_names[idx])

    # domain_scores: average similarity of job to sample resumes grouped by predicted domain
    domain_to_sims = {}
    if sample_vecs.shape[0] > 0:
        sims = cosine_similarity(job_vec, sample_vecs)[0]  # len = num_samples
        preds = model.predict(sample_vecs)
        for domain, sim in zip(preds, sims):
            domain_to_sims.setdefault(domain, []).append(sim)
        domain_scores = []
        for domain, sim_list in domain_to_sims.items():
            avg = float(np.mean(sim_list)) * 100.0
            domain_scores.append((domain, round(avg, 2)))
        domain_scores = sorted(domain_scores, key=lambda x: x[1], reverse=True)[:6]
    else:
        domain_scores = [(pred_uploaded, round(overall_match_pct, 2))]

    # create charts
    bar_chart_b64 = _plot_bar_domain_scores(domain_scores)
    pie_chart_b64 = _plot_pie(overall_match_pct)

    return {
        "overall_match": overall_match_pct,
        "predicted_domain": str(pred_uploaded),
        "top_keywords": top_keywords,
        "missing_keywords": missing_keywords,
        "domain_scores": domain_scores,
        "bar_chart": bar_chart_b64,
        "pie_chart": pie_chart_b64,
        "summary": build_summary(overall_match_pct, pred_uploaded, top_keywords, missing_keywords)
    }

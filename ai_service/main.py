from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import joblib
import os
import pandas as pd

# Create the FastAPI app
app = FastAPI(title="Resume Classification API", version="1.0")

# Allow frontend (React) and backend (Node/FastAPI) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can later restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths for saved model and vectorizer
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "resume_match.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "model", "tfidf_vectorizer.pkl")

# Load model and vectorizer
model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


@app.get("/")
def home():
    return {"message": "Resume Classification API is running successfully 🚀"}


@app.post("/predict/")
async def predict_resume_category(text: str = Form(...)):
    """
    Endpoint to classify a given resume text into a category.
    """
    try:
        # Convert text to vector
        input_data = vectorizer.transform([text])

        # Predict category
        prediction = model.predict(input_data)[0]

        return {"predicted_category": prediction}

    except Exception as e:
        return {"error": str(e)}


# Optional: if you want to upload a text file instead of plain text input
@app.post("/predict_file/")
async def predict_from_file(file: UploadFile):
    try:
        contents = await file.read()
        text = contents.decode("utf-8")

        input_data = vectorizer.transform([text])
        prediction = model.predict(input_data)[0]

        return {"predicted_category": prediction}

    except Exception as e:
        return {"error": str(e)}

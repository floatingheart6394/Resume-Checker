# AI Service

This module contains all the machine learning and text-processing logic for the Resume Checker application.

It handles:
- Resume text extraction
- Job description text processing
- TF-IDF vectorization
- Cosine similarity scoring
- Naive Bayes domain prediction
- ML model loading & classification utilities

---

## 📁 Folder Structure
ai_service/
├── data/
│ ├── job_descriptions/ # Example job descriptions (training data)
│ ├── resumes/ # Example resumes (training data)
│ └── sample_resumes/ # Used for testing
├── model/
│ └── model.pkl # Trained Naive Bayes model
│ └── vectorizer.pkl # TF-IDF vectorizer
├── init.py
└── main.py # Core AI functions (scoring + prediction)


---

## 🧠 How the AI Works

### 1️⃣ Text Extraction  
- Uses **PyMuPDF (fitz)** for PDF  
- Uses **python-docx** for DOCX  
- Uses simple read for TXT  

### 2️⃣ Pre-processing  
- Lowercasing  
- Removing special characters  
- Removing extra spaces  
- Tokenization  
- Stopword removal  

### 3️⃣ TF-IDF Vectorization  
The job description and resume are converted to numerical vectors using TF-IDF.

### 4️⃣ Cosine Similarity  
Calculates match percentage between vectors.

### 5️⃣ Naive Bayes Domain Prediction  
Predicts resume domain:  
- Machine Learning  
- Data Science  
- Web Development  
- Cybersecurity  
- etc.  
(Depends on your training data.)

---

## ▶️ Running the AI Service Alone (for testing)

Start Python shell:


Then:

```python
from ai_service.main import match_resume

result = match_resume("resume text...", "job description...")
print(result)

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

# Load dataset (adjust filename if different)
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'resumes','UpdatedResumeDataSet.csv')

print(f"Loading dataset from: {DATA_PATH}")
data = pd.read_csv(DATA_PATH)

# Check columns — assume dataset has 'Category' and 'Resume' columns
print("Columns found:", data.columns)

# Clean missing data
data = data.dropna(subset=['Category', 'Resume'])

# Split data
X = data['Resume']
y = data['Category']

# Convert text to TF-IDF features
print("Vectorizing text data...")
vectorizer = TfidfVectorizer(stop_words='english', max_features=3000)
X_vect = vectorizer.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_vect, y, test_size=0.2, random_state=42)

# Train Naive Bayes model
print("Training Naive Bayes classifier...")
model = MultinomialNB()
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Model trained successfully with accuracy: {acc:.2f}")

# Save model and vectorizer
MODEL_DIR = os.path.join(os.path.dirname(__file__))
joblib.dump(model, os.path.join(MODEL_DIR, 'resume_match.pkl'))
joblib.dump(vectorizer, os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl'))

print("Model and vectorizer saved successfully!")

import os
import pandas as pd

# Define paths
BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "resumes", "Resume.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "sample_resumes")

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read the dataset
print(f"Loading dataset from: {CSV_PATH}")
data = pd.read_csv(CSV_PATH, encoding='utf-8')

# Check if the expected columns exist
if "Resume_str" not in data.columns:
    raise KeyError("The dataset must contain a column named 'Resume_str'.")

print(f"Found {len(data)} resumes. Extracting...")

# Save each resume as a separate text file
saved_count = 0
for i, text in enumerate(data["Resume_str"]):
    if isinstance(text, str) and len(text.strip()) > 100:  # skip short or empty ones
        resume_path = os.path.join(OUTPUT_DIR, f"resume_{i+1}.txt")
        with open(resume_path, "w", encoding="utf-8") as f:
            f.write(text.strip())
        saved_count += 1

print(f"Successfully extracted {saved_count} resumes to: {OUTPUT_DIR}")
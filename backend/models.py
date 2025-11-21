# backend/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ResumeRecord(Base):
    __tablename__ = "resume_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    resume_text = Column(Text, nullable=True)
    resume_file_url = Column(String, nullable=True)
    job_description = Column(Text, nullable=True)
    predicted_domain = Column(String, nullable=True)
    match_score = Column(String, nullable=True)
    matched_keywords = Column(Text, nullable=True)
    missing_keywords = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

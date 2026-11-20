from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, LargeBinary, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="doctor")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="user")
    login_logs = relationship("LoginLog", back_populates="user")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    contact = Column(String(50))
    address = Column(Text)
    medical_history = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="patient")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    image_path = Column(String(500), nullable=False)
    original_filename = Column(String(255))
    predictions = Column(JSON, nullable=False)
    confidence_scores = Column(JSON, nullable=False)
    severity = Column(String(50))
    model_used = Column(String(100))
    inference_time = Column(Float)
    grad_cam_path = Column(String(500))
    is_healthy = Column(Boolean, default=False)
    clinical_impression = Column(Text)
    recommendations = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="predictions")
    patient = relationship("Patient", back_populates="predictions")
    reports = relationship("Report", back_populates="prediction")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False)
    report_path = Column(String(500))
    findings = Column(Text)
    impression = Column(Text)
    recommendations = Column(Text)
    doctor_notes = Column(Text)
    generated_at = Column(DateTime, default=datetime.utcnow)

    prediction = relationship("Prediction", back_populates="reports")


class LoginLog(Base):
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    login_time = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)

    user = relationship("User", back_populates="login_logs")


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

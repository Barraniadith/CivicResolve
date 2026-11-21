from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(32), primary_key=True, index=True) # e.g. CIV-2026-1001
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    location_name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    image_url = Column(String(500), nullable=True)
    
    citizen_name = Column(String(100), default="Anonymous Citizen")
    citizen_phone = Column(String(20), nullable=True)
    
    # AI-Derived & Triage Attributes
    category = Column(String(100), nullable=False) # e.g., Potholes & Road Damage, Garbage, etc.
    urgency = Column(String(20), default="Medium") # Low, Medium, High, Critical
    public_impact_score = Column(Integer, default=3) # 1 to 5
    department = Column(String(150), nullable=False)
    ai_confidence = Column(Float, default=0.85)
    ai_reasoning = Column(Text, nullable=True)
    
    # Workflow Status
    status = Column(String(50), default="Reported") # Reported, In Progress, Resolved
    assigned_officer = Column(String(100), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    resolution_image_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    logs = relationship("AuditLog", back_populates="complaint", cascade="all, delete-orphan", order_by="AuditLog.timestamp.desc()")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(String(32), ForeignKey("complaints.id"), nullable=False)
    action = Column(String(100), nullable=False) # SUBMITTED, AI_TRIAGED, STATUS_UPDATED, REASSIGNED
    actor = Column(String(100), default="System") # Citizen, Gemini AI Engine, Municipal Officer
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="logs")

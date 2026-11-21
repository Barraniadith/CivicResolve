from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AuditLogResponse(BaseModel):
    id: int
    complaint_id: str
    action: str
    actor: str
    details: Optional[str] = None
    timestamp: str

    class Config:
        from_attributes = True

class ComplaintBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    location_name: str = Field(..., min_length=2, max_length=255)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    citizen_name: Optional[str] = "Anonymous Citizen"
    citizen_phone: Optional[str] = None
    category: Optional[str] = None
    urgency: Optional[str] = "Medium"
    department: Optional[str] = None

class ComplaintCreate(ComplaintBase):
    pass

class RatingRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None

class ComplaintResponse(BaseModel):
    id: str
    title: str
    description: str
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    citizen_name: Optional[str] = None
    citizen_phone: Optional[str] = None
    category: str
    urgency: str
    public_impact_score: int
    department: str
    ai_confidence: float
    ai_reasoning: Optional[str] = None
    status: str
    assigned_officer: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolution_image_url: Optional[str] = None
    upvotes: int = 1
    satisfaction_rating: Optional[int] = None
    created_at: str
    updated_at: str
    logs: List[AuditLogResponse] = []

    class Config:
        from_attributes = True

class StatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(Reported|In Progress|Resolved)$")
    assigned_officer: Optional[str] = None
    notes: Optional[str] = None
    resolution_image_url: Optional[str] = None
    department: Optional[str] = None

class AIPreviewRequest(BaseModel):
    title: Optional[str] = ""
    description: str
    location_name: Optional[str] = "Coimbatore"
    image_data_base64: Optional[str] = None
    language: Optional[str] = "en" # 'en' or 'ta'

class AIPreviewResponse(BaseModel):
    category: str
    urgency: str
    public_impact_score: int
    department: str
    confidence: float
    reasoning: str
    suggested_title: Optional[str] = None
    title_ta: Optional[str] = None
    hazard_flags: List[str] = []
    is_fallback: bool = False
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None

class StatsResponse(BaseModel):
    total_complaints: int
    reported_count: int
    in_progress_count: int
    resolved_count: int
    critical_count: int
    high_count: int
    department_breakdown: Dict[str, int]
    category_breakdown: Dict[str, int]
    avg_satisfaction: Optional[float] = 4.8

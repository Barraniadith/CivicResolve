import os
import shutil
import uuid
import random
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, UploadFile, File

from ..database import (
    fetch_all_complaints,
    fetch_complaint_by_id,
    insert_complaint,
    insert_audit_log,
    update_complaint_fields,
    upvote_complaint,
    rate_complaint_resolution,
    count_complaints
)
from ..schemas import ComplaintCreate, ComplaintResponse, StatusUpdateRequest, RatingRequest
from ..ai_service import analyze_grievance_with_gemini, DEPARTMENTS

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# City & Landmark Coordinates Reference
CITY_COORDINATES = {
    "coimbatore": (11.0168, 76.9558),
    "chennai": (13.0827, 80.2707),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "madurai": (9.9252, 78.1198),
    "tiruppur": (11.1085, 77.3411),
    "salem": (11.6643, 78.1460),
    "trichy": (10.7905, 78.7047),
    "tiruchirappalli": (10.7905, 78.7047),
    "hyderabad": (17.3850, 78.4867),
    "kochi": (9.9312, 76.2673),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090)
}

SPECIFIC_LANDMARKS = {
    "psg itech": (11.0543, 77.0862),
    "neelambur": (11.0612, 77.0984),
    "peelamedu": (11.0321, 77.0019),
    "aerodrome": (11.0289, 77.0392),
    "singanallur": (10.9984, 77.0193),
    "gandhipuram": (11.0183, 76.9667),
    "rs puram": (11.0084, 76.9452),
    "omr": (12.9249, 80.2299),
    "silk board": (12.9176, 77.6238),
    "anna nagar": (13.0850, 80.2101),
    "indiranagar": (12.9784, 77.6408)
}

def resolve_coordinates(location_name: str, given_lat: Optional[float], given_lng: Optional[float]):
    if given_lat and given_lng and given_lat != 0 and given_lng != 0:
        return given_lat, given_lng

    loc_lower = (location_name or "").lower()
    
    # Check specific landmark keywords
    for landmark, coords in SPECIFIC_LANDMARKS.items():
        if landmark in loc_lower:
            # Add small random jitter so pins don't overlap completely
            jitter_lat = coords[0] + random.uniform(-0.002, 0.002)
            jitter_lng = coords[1] + random.uniform(-0.002, 0.002)
            return round(jitter_lat, 5), round(jitter_lng, 5)

    # Check city keywords
    for city, coords in CITY_COORDINATES.items():
        if city in loc_lower:
            jitter_lat = coords[0] + random.uniform(-0.015, 0.015)
            jitter_lng = coords[1] + random.uniform(-0.015, 0.015)
            return round(jitter_lat, 5), round(jitter_lng, 5)

    # Default fallback to Coimbatore / Neelambur region
    return (
        round(11.0543 + random.uniform(-0.02, 0.02), 5),
        round(77.0862 + random.uniform(-0.02, 0.02), 5)
    )

@router.get("", response_model=List[ComplaintResponse])
def get_complaints(
    status: Optional[str] = Query(None, description="Filter by status: Reported, In Progress, Resolved"),
    urgency: Optional[str] = Query(None, description="Filter by urgency: Critical, High, Medium, Low"),
    department: Optional[str] = Query(None, description="Filter by department"),
    search: Optional[str] = Query(None, description="Search keyword in title, description, or location")
):
    return fetch_all_complaints(status=status, urgency=urgency, department=department, search=search)


@router.post("", response_model=ComplaintResponse)
def create_complaint(payload: ComplaintCreate):
    count = count_complaints() + 1
    new_id = f"CIV-2026-{1000 + count}"

    category = payload.category
    urgency = payload.urgency or "Medium"
    department = payload.department
    impact = 3
    confidence = 0.88
    reasoning = "Civic grievance registered by citizen."

    # If AI triage wasn't run on frontend, run it now
    if not category or not department or category == "Pending AI":
        ai_res = analyze_grievance_with_gemini(
            title=payload.title,
            description=payload.description,
            location_name=payload.location_name
        )
        category = ai_res.get("category", "Other Civic Grievance")
        urgency = ai_res.get("urgency", "Medium")
        impact = ai_res.get("public_impact_score", 3)
        department = ai_res.get("department", DEPARTMENTS.get(category, "Public Grievance Redressal Cell"))
        confidence = ai_res.get("confidence", 0.85)
        reasoning = ai_res.get("reasoning", "")

    now_iso = datetime.utcnow().isoformat()

    lat, lng = resolve_coordinates(payload.location_name, payload.latitude, payload.longitude)

    complaint_data = {
        "id": new_id,
        "title": payload.title,
        "description": payload.description,
        "location_name": payload.location_name,
        "latitude": lat,
        "longitude": lng,
        "image_url": payload.image_url,
        "citizen_name": payload.citizen_name or "Anonymous Citizen",
        "citizen_phone": payload.citizen_phone,
        "category": category,
        "urgency": urgency,
        "public_impact_score": impact,
        "department": department,
        "ai_confidence": confidence,
        "ai_reasoning": reasoning,
        "status": "Reported",
        "assigned_officer": None,
        "resolution_notes": None,
        "resolution_image_url": None,
        "upvotes": 1,
        "satisfaction_rating": None,
        "created_at": now_iso,
        "updated_at": now_iso
    }

    comp = insert_complaint(complaint_data)

    insert_audit_log(
        complaint_id=new_id,
        action="SUBMITTED",
        actor=payload.citizen_name or "Citizen",
        details=f"Complaint lodged for {payload.location_name}.",
        timestamp=now_iso
    )
    insert_audit_log(
        complaint_id=new_id,
        action="AI_TRIAGED",
        actor="Google Gemini AI Engine",
        details=f"Classified as '{category}' ({urgency} Urgency). Routed to '{department}'.",
        timestamp=now_iso
    )

    return fetch_complaint_by_id(new_id)


@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(complaint_id: str):
    comp = fetch_complaint_by_id(complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return comp


@router.patch("/{complaint_id}/status", response_model=ComplaintResponse)
def update_complaint_status(
    complaint_id: str,
    payload: StatusUpdateRequest
):
    comp = fetch_complaint_by_id(complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")

    old_status = comp["status"]
    updates = {"status": payload.status}

    if payload.assigned_officer:
        updates["assigned_officer"] = payload.assigned_officer
    if payload.notes:
        updates["resolution_notes"] = payload.notes
    if payload.resolution_image_url:
        updates["resolution_image_url"] = payload.resolution_image_url
    if payload.department:
        updates["department"] = payload.department

    update_complaint_fields(complaint_id, updates)

    action_type = "STATUS_UPDATED"
    if payload.status == "Resolved":
        action_type = "RESOLVED"
    elif payload.status == "In Progress":
        action_type = "WORK_COMMENCED"

    officer_name = payload.assigned_officer or "Municipal Admin"
    details = f"Status changed from '{old_status}' to '{payload.status}'."
    if payload.notes:
        details += f" Officer note: {payload.notes}"

    insert_audit_log(
        complaint_id=complaint_id,
        action=action_type,
        actor=officer_name,
        details=details
    )

    return fetch_complaint_by_id(complaint_id)


@router.post("/{complaint_id}/upvote", response_model=ComplaintResponse)
def upvote(complaint_id: str):
    """Community Upvote / 'Me Too' counter increment."""
    comp = upvote_complaint(complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return comp


@router.post("/{complaint_id}/rate", response_model=ComplaintResponse)
def rate_resolution(complaint_id: str, payload: RatingRequest):
    """Citizen rating on resolved ticket."""
    comp = rate_complaint_resolution(complaint_id, payload.rating, payload.feedback)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return comp


@router.post("/upload-image")
async def upload_complaint_image(file: UploadFile = File(...)):
    """Uploads grievance photo to local storage."""
    allowed_exts = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        ext = ".jpg"

    filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, filename)

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": filename,
        "image_url": f"/uploads/{filename}",
        "success": True
    }

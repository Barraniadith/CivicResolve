from fastapi import APIRouter
from ..schemas import AIPreviewRequest, AIPreviewResponse
from ..ai_service import analyze_grievance_with_gemini

router = APIRouter(prefix="/api/ai", tags=["AI Triage"])

@router.post("/preview", response_model=AIPreviewResponse)
def preview_ai_triage(payload: AIPreviewRequest):
    """
    Live real-time AI triage preview endpoint.
    Called on citizen form interaction or photo upload so the citizen can see
    how Google Gemini understands the issue, assigns urgency, and routes it
    before hitting final submit.
    """
    result = analyze_grievance_with_gemini(
        title=payload.title or "",
        description=payload.description,
        location_name=payload.location_name or "Coimbatore",
        image_base64=payload.image_data_base64
    )

    return AIPreviewResponse(
        category=result.get("category", "Other Civic Grievance"),
        urgency=result.get("urgency", "Medium"),
        public_impact_score=result.get("public_impact_score", 3),
        department=result.get("department", "CCMC - Public Grievance Redressal Cell"),
        confidence=result.get("confidence", 0.85),
        reasoning=result.get("reasoning", ""),
        suggested_title=result.get("suggested_title"),
        hazard_flags=result.get("hazard_flags", []),
        is_fallback=result.get("is_fallback", False)
    )

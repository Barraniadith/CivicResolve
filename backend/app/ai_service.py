import os
import re
import json
import base64
from io import BytesIO
from functools import lru_cache
from typing import Dict, Any, Optional

# Supported Civic Categories
CATEGORIES = [
    "Potholes & Road Damage",
    "Garbage & Sanitation",
    "Streetlights & Electrical",
    "Water Leakage & Sewage",
    "Drainage & Waterlogging",
    "Public Infrastructure & Parks",
    "Other Civic Grievance"
]

# Municipal Department Directory
DEPARTMENTS = {
    "Potholes & Road Damage": "Coimbatore City Municipal Corporation (CCMC) - Roads & Bridges",
    "Garbage & Sanitation": "CCMC - Solid Waste Management & Sanitation",
    "Streetlights & Electrical": "Tamil Nadu Generation and Distribution Corporation (TANGEDCO) - Streetlights",
    "Water Leakage & Sewage": "Tamil Nadu Water Supply and Drainage Board (TWAD)",
    "Drainage & Waterlogging": "CCMC - Stormwater Drainage Division",
    "Public Infrastructure & Parks": "CCMC - Parks & Urban Amenities",
    "Other Civic Grievance": "CCMC - Public Grievance Redressal Cell"
}

@lru_cache(maxsize=256)
def _cached_heuristic_calc(title: str, description: str, location: str) -> str:
    """Internal LRU-cached heuristic execution returning JSON string."""
    text = f"{title} {description} {location}".lower()
    
    # Category Matching
    category = "Other Civic Grievance"
    urgency = "Medium"
    impact = 3
    hazard_flags = []

    if any(k in text for k in ["pothole", "crater", "asphalt", "road damage", "tar road", "craters", "uneven road", "speed breaker"]):
        category = "Potholes & Road Damage"
        if any(k in text for k in ["deep", "huge", "accident", "swerve", "highway", "main road", "traffic", "avinashi"]):
            urgency = "High"
            impact = 4
            hazard_flags.append("traffic_swerving_risk")
    elif any(k in text for k in ["garbage", "trash", "waste", "dump", "bin", "overflowing", "smell", "odor", "litter", "debris"]):
        category = "Garbage & Sanitation"
        if any(k in text for k in ["maggots", "disease", "toxic", "blocking", "hospital", "school"]):
            urgency = "High"
            impact = 4
            hazard_flags.append("health_sanitation_hazard")
    elif any(k in text for k in ["light", "streetlight", "lamp", "dark", "wire", "electric", "sparking", "tangedco", "pole"]):
        category = "Streetlights & Electrical"
        if any(k in text for k in ["wire", "sparking", "hanging", "shock", "live wire", "open wire"]):
            urgency = "Critical"
            impact = 5
            hazard_flags.extend(["electrocution_risk", "public_safety_emergency"])
        elif any(k in text for k in ["dark", "junction", "women safety", "night"]):
            urgency = "High"
            impact = 3
            hazard_flags.append("nighttime_visibility_hazard")
    elif any(k in text for k in ["water", "leak", "pipe", "burst", "pipeline", "drinking water", "twad"]):
        category = "Water Leakage & Sewage"
        if any(k in text for k in ["burst", "gushing", "flood", "contamination", "drinking water wasted"]):
            urgency = "High"
            impact = 4
            hazard_flags.append("resource_wastage_road_softening")
    elif any(k in text for k in ["drain", "drainage", "sewage", "gutter", "waterlog", "flood", "stagnant"]):
        category = "Drainage & Waterlogging"
        if any(k in text for k in ["flood", "entering house", "submerged", "mosquitos"]):
            urgency = "High"
            impact = 4
            hazard_flags.append("waterborne_disease_risk")
    elif any(k in text for k in ["park", "bench", "fence", "tree", "fallen tree", "footpath", "pavement"]):
        category = "Public Infrastructure & Parks"
        if any(k in text for k in ["fallen tree", "blocking road"]):
            urgency = "High"
            impact = 4
            hazard_flags.append("traffic_blockage")

    department = DEPARTMENTS.get(category, "CCMC - Public Grievance Redressal Cell")
    
    suggested_title = title.strip()
    if not suggested_title or len(suggested_title) < 5:
        suggested_title = f"{category} reported at {location or 'locality'}"

    reasoning = (
        f"Automated civic triage identified keywords relating to {category.lower()} at {location or 'locality'}. "
        f"Assigned urgency '{urgency}' with public impact {impact}/5 due to detected hazards ({', '.join(hazard_flags) or 'standard civic disruption'}). "
        f"Routed to {department}."
    )

    data = {
        "category": category,
        "urgency": urgency,
        "public_impact_score": impact,
        "department": department,
        "confidence": 0.82,
        "reasoning": reasoning,
        "suggested_title": suggested_title,
        "hazard_flags": hazard_flags,
        "is_fallback": True
    }
    return json.dumps(data)

def analyze_with_heuristics(title: str, description: str, location: str) -> Dict[str, Any]:
    """
    Intelligent local heuristic fallback engine backed by an in-memory LRU cache.
    Ensures 100% demo uptime and sub-millisecond efficiency.
    """
    res_str = _cached_heuristic_calc(
        (title or "").strip().lower(),
        (description or "").strip().lower(),
        (location or "").strip().lower()
    )
    return json.loads(res_str)


def analyze_grievance_with_gemini(
    title: str,
    description: str,
    location_name: str,
    image_base64: Optional[str] = None
) -> Dict[str, Any]:
    """
    Invokes Google Gemini via the official google-genai SDK to perform multimodal or text-based
    civic grievance classification, priority detection, and municipal department routing.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        # Graceful fallback when user has not yet configured GEMINI_API_KEY
        fallback = analyze_with_heuristics(title, description, location_name)
        fallback["reasoning"] += " (Heuristic AI Mode: Add GEMINI_API_KEY to backend/.env for Gemini 2.5 Flash live inference)"
        return fallback

    prompt = f"""
You are the AI Triage Engine for "CivicResolve", an intelligent municipal grievance resolution system for Coimbatore / Tamil Nadu.
Analyze the following citizen-reported civic issue and produce a strictly compliant JSON object.

Incident Details:
- Title: {title or 'Unspecified'}
- Location: {location_name or 'Coimbatore'}
- Citizen Description: {description}

Categories allowed (choose exactly one):
1. Potholes & Road Damage
2. Garbage & Sanitation
3. Streetlights & Electrical
4. Water Leakage & Sewage
5. Drainage & Waterlogging
6. Public Infrastructure & Parks
7. Other Civic Grievance

Urgency levels allowed (choose exactly one):
- Critical: Immediate risk of life, electrocution, deep open manhole/sinkhole, emergency route blocked.
- High: Major arterial road hazard, overflowing sewage, burst water main, dark accident-prone junction.
- Medium: General uncollected garbage, moderate pothole on residential road, leaking valve.
- Low: Cosmetic wear, faded street sign, minor park maintenance.

Department choices:
- Coimbatore City Municipal Corporation (CCMC) - Roads & Bridges
- CCMC - Solid Waste Management & Sanitation
- Tamil Nadu Generation and Distribution Corporation (TANGEDCO) - Streetlights
- Tamil Nadu Water Supply and Drainage Board (TWAD)
- CCMC - Stormwater Drainage Division
- CCMC - Parks & Urban Amenities
- CCMC - Public Grievance Redressal Cell

Your response must be ONLY a valid JSON object with these keys:
{{
  "category": "<Exact category name from list>",
  "urgency": "<Critical | High | Medium | Low>",
  "public_impact_score": <Integer from 1 to 5>,
  "department": "<Exact department name from list>",
  "confidence": <Float between 0.70 and 0.99>,
  "suggested_title": "<Concise 4-8 word descriptive title>",
  "hazard_flags": ["<tag1>", "<tag2>"],
  "reasoning": "<2-3 sentence municipal triage reasoning explaining urgency, public safety risks, and why this specific department was selected>"
}}
"""

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        
        contents = [prompt]

        # Handle multimodal image if provided
        if image_base64:
            # Strip header if data URI
            clean_b64 = image_base64
            mime_type = "image/jpeg"
            if "data:" in clean_b64 and ";base64," in clean_b64:
                header, clean_b64 = clean_b64.split(";base64,")
                if "image/png" in header:
                    mime_type = "image/png"
                elif "image/webp" in header:
                    mime_type = "image/webp"

            image_bytes = base64.b64decode(clean_b64)
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            contents.append(image_part)

        # Use gemini-2.5-flash or gemini-1.5-flash
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )

        response_text = response.text.strip()
        # Clean markdown codeblocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        parsed = json.loads(response_text.strip())
        parsed["is_fallback"] = False
        return parsed

    except Exception as e:
        print(f"[Gemini AI Triage Warning] {e}. Falling back to resilient heuristic triage.")
        fallback = analyze_with_heuristics(title, description, location_name)
        fallback["reasoning"] += f" (Gemini API notification: {str(e)[:90]}... Evaluated via local AI heuristics)"
        return fallback

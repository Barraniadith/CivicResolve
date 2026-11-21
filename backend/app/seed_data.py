from datetime import datetime, timedelta
from .database import (
    count_complaints,
    insert_complaint,
    insert_audit_log
)

SEED_COMPLAINTS = [
    {
        "id": "CIV-2026-1001",
        "title": "Severe Pothole Cluster near PSG iTech Main Gate",
        "description": "Deep asphalt crater (approx 2 feet wide, 5 inches deep) on the inbound Avinashi Road lane right outside PSG iTech campus. Two-wheelers are violently swerving into heavy bus traffic to avoid tire puncture.",
        "location_name": "PSG iTech Main Gate, Neelambur (Avinashi Road)",
        "latitude": 11.0543,
        "longitude": 77.0862,
        "image_url": "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800&auto=format&fit=crop&q=60",
        "citizen_name": "Karthik Subramanian",
        "citizen_phone": "+91 98421 12345",
        "category": "Potholes & Road Damage",
        "urgency": "High",
        "public_impact_score": 4,
        "department": "Coimbatore City Municipal Corporation (CCMC) - Roads & Bridges",
        "ai_confidence": 0.96,
        "ai_reasoning": "Gemini Multimodal Analysis detected deep structural bitumen damage on high-speed arterial corridor (Avinashi Rd). High vehicular swerving hazard identified for college commuters and public transport.",
        "status": "Reported",
        "assigned_officer": None,
        "resolution_notes": None,
        "resolution_image_url": None,
        "created_at": (datetime.utcnow() - timedelta(hours=4)).isoformat(),
        "updated_at": (datetime.utcnow() - timedelta(hours=4)).isoformat()
    },
    {
        "id": "CIV-2026-1002",
        "title": "Overflowing Dumper Bins & Scattered Medical Waste",
        "description": "Four secondary municipal garbage bins are overflowing across 20 meters of pavement near Peelamedu weekly market. Foul odor, stray cattle hazard, and stray dogs scattering rotting organic waste into the road.",
        "location_name": "Peelamedu Market Road, Ward 24, Coimbatore",
        "latitude": 11.0321,
        "longitude": 77.0019,
        "image_url": "https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=800&auto=format&fit=crop&q=60",
        "citizen_name": "Priya Natarajan",
        "citizen_phone": "+91 94432 87654",
        "category": "Garbage & Sanitation",
        "urgency": "High",
        "public_impact_score": 4,
        "department": "CCMC - Solid Waste Management & Sanitation",
        "ai_confidence": 0.94,
        "ai_reasoning": "High sanitation vector hazard. Visual analysis identified solid organic refuse blocking pedestrian thoroughfare in dense commercial zone. Assigned to CCMC Ward 24 Sanitation Rapid Team.",
        "status": "In Progress",
        "assigned_officer": "R. Selvaraj (Sanitation Inspector)",
        "resolution_notes": "Compactor truck CP-14 dispatched. Manual clearing underway with bleaching powder sanitization.",
        "resolution_image_url": None,
        "created_at": (datetime.utcnow() - timedelta(hours=14)).isoformat(),
        "updated_at": (datetime.utcnow() - timedelta(hours=2)).isoformat()
    },
    {
        "id": "CIV-2026-1003",
        "title": "Broken Streetlight with Exposed Sparking Cable",
        "description": "Metal streetlight pole tilted at a 40-degree angle after a mini-truck hit it last night. Live 230V overhead supply wires are drooping 6 feet from the pedestrian walkway, sparking during light rain.",
        "location_name": "Neelambur Bypass Junction, Coimbatore",
        "latitude": 11.0612,
        "longitude": 77.0984,
        "image_url": "https://images.unsplash.com/photo-1508873696983-2df5293cb32b?w=800&auto=format&fit=crop&q=60",
        "citizen_name": "Dinesh Kumar (Student, PSG iTech)",
        "citizen_phone": "+91 97900 65432",
        "category": "Streetlights & Electrical",
        "urgency": "Critical",
        "public_impact_score": 5,
        "department": "Tamil Nadu Generation and Distribution Corporation (TANGEDCO) - Streetlights",
        "ai_confidence": 0.98,
        "ai_reasoning": "CRITICAL LIFE-SAFETY HAZARD. Automated triage flagged exposed live electrical conductor in public right-of-way during wet monsoon conditions. Immediate feeder shutdown requested.",
        "status": "Reported",
        "assigned_officer": None,
        "resolution_notes": None,
        "resolution_image_url": None,
        "created_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
        "updated_at": (datetime.utcnow() - timedelta(hours=1)).isoformat()
    },
    {
        "id": "CIV-2026-1004",
        "title": "Major Drinking Water Main Pipe Burst",
        "description": "Underground 300mm Bhavani drinking water distribution pipe ruptured. Clean drinking water is gushing under high pressure, flooding half the road and eroding foundation sub-base near Civil Aerodrome.",
        "location_name": "Civil Aerodrome Road, SIHS Colony, Coimbatore",
        "latitude": 11.0289,
        "longitude": 77.0392,
        "image_url": "https://images.unsplash.com/photo-1541888946425-d0fbb186f5f7?w=800&auto=format&fit=crop&q=60",
        "citizen_name": "Anand Mohan",
        "citizen_phone": "+91 98940 33211",
        "category": "Water Leakage & Sewage",
        "urgency": "High",
        "public_impact_score": 4,
        "department": "Tamil Nadu Water Supply and Drainage Board (TWAD)",
        "ai_confidence": 0.92,
        "ai_reasoning": "Severe potable water loss detected at rate >15,000 L/hr. Ground erosion threatens adjacent underground telecom ducts. Escalated to TWAD East Maintenance division.",
        "status": "In Progress",
        "assigned_officer": "K. Murugan (Executive Engineer TWAD)",
        "resolution_notes": "Sluice valve #12 isolated to prevent further flooding. Heavy excavation JCB dispatched for pipe sleeve clamp.",
        "resolution_image_url": None,
        "created_at": (datetime.utcnow() - timedelta(hours=8)).isoformat(),
        "updated_at": (datetime.utcnow() - timedelta(hours=3)).isoformat()
    },
    {
        "id": "CIV-2026-1005",
        "title": "Stagnant Stormwater Drain Clogging & Silt Deposition",
        "description": "Concrete stormwater channel completely clogged with plastic bottles and construction silt. Black stagnant water backed up into residential lane during yesterday's evening thunderstorm.",
        "location_name": "Singanallur Trichy Road Intersection, Coimbatore",
        "latitude": 10.9984,
        "longitude": 77.0193,
        "image_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800&auto=format&fit=crop&q=60",
        "citizen_name": "Lakshmi Ramanathan",
        "citizen_phone": "+91 94441 98765",
        "category": "Drainage & Waterlogging",
        "urgency": "Medium",
        "public_impact_score": 3,
        "department": "CCMC - Stormwater Drainage Division",
        "ai_confidence": 0.91,
        "ai_reasoning": "High waterlogging risk. Drain choked by debris. Triage categorized under CCMC Stormwater Drainage. Silt dredging scheduled.",
        "status": "Resolved",
        "assigned_officer": "V. Gunasekaran (Junior Engineer, Drainage)",
        "resolution_notes": "Drainage de-silting machine utilized to extract 3.2 tons of choked silt and plastic waste. Free-flowing drainage restored. Photo verified.",
        "resolution_image_url": "https://images.unsplash.com/photo-1584467735871-8e85353a8413?w=800&auto=format&fit=crop&q=60",
        "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
        "updated_at": (datetime.utcnow() - timedelta(hours=10)).isoformat()
    }
]

def seed_database():
    if count_complaints() > 0:
        return

    for data in SEED_COMPLAINTS:
        insert_complaint(data)

        # Audit logs
        c_time = data["created_at"]
        insert_audit_log(
            data["id"],
            "SUBMITTED",
            data.get("citizen_name", "Citizen"),
            "Grievance lodged via CivicResolve Mobile Portal.",
            c_time
        )
        insert_audit_log(
            data["id"],
            "AI_TRIAGED",
            "Google Gemini AI Engine",
            f"Assigned Category: '{data['category']}', Urgency: '{data['urgency']}', Department: '{data['department']}'. Confidence: {int(data['ai_confidence']*100)}%",
            c_time
        )

        if data["status"] in ["In Progress", "Resolved"]:
            insert_audit_log(
                data["id"],
                "ASSIGNED",
                "CCMC Dispatch Console",
                f"Dispatched to officer: {data['assigned_officer']}",
                c_time
            )

        if data["status"] == "Resolved":
            insert_audit_log(
                data["id"],
                "RESOLVED",
                data.get("assigned_officer", "Municipal Engineer"),
                data.get("resolution_notes", "Field repair completed and verified."),
                data["updated_at"]
            )

    print("[CivicResolve] Pre-seeded 5 realistic grievances with AI triage metadata.")

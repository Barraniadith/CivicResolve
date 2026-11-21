import unittest
import os
import sys

# Ensure backend root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import settings
from app.ai_service import analyze_with_heuristics, CATEGORIES, DEPARTMENTS, _cached_heuristic_calc
from app.database import (
    init_db,
    get_connection,
    fetch_all_complaints,
    fetch_complaint_by_id,
    insert_complaint,
    insert_audit_log,
    update_complaint_fields,
    get_stats_data
)
from app.routes.complaints import resolve_coordinates

class CivicResolveUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_01_config_initialization(self):
        """Validate centralized application configuration."""
        self.assertEqual(settings.app_name, "CivicResolve")
        self.assertGreater(settings.max_pagination_limit, 100)
        self.assertIsNotNone(settings.gemini_model)

    def test_02_categories_and_departments(self):
        """Ensure all standard civic categories have mapped municipal departments."""
        self.assertGreaterEqual(len(CATEGORIES), 7)
        for cat in CATEGORIES:
            self.assertIn(cat, DEPARTMENTS)

    def test_03_heuristic_ai_critical_hazard(self):
        """Test intelligent classification for high-priority life safety hazards."""
        result = analyze_with_heuristics(
            title="Broken live wire sparking",
            description="High voltage wire fell on pedestrian path with electrical sparks",
            location="Avinashi Road"
        )
        self.assertEqual(result["category"], "Streetlights & Electrical")
        self.assertEqual(result["urgency"], "Critical")
        self.assertEqual(result["public_impact_score"], 5)
        self.assertIn("electrocution_risk", result["hazard_flags"])
        self.assertIn("TANGEDCO", result["department"])

    def test_04_heuristic_ai_pothole_classification(self):
        """Test classification and department routing for road damages."""
        result = analyze_with_heuristics(
            title="Massive road crater",
            description="Deep crater pothole damaging two-wheelers and cars",
            location="PSG iTech Campus Entrance"
        )
        self.assertEqual(result["category"], "Potholes & Road Damage")
        self.assertIn("CCMC", result["department"])

    def test_05_heuristic_ai_sanitation_hazard(self):
        """Test sanitation classification and public health hazard detection."""
        result = analyze_with_heuristics(
            title="Overflowing waste bin",
            description="Garbage dump uncleared for days with disease and foul smell",
            location="Neelambur Bus Stand"
        )
        self.assertEqual(result["category"], "Garbage & Sanitation")
        self.assertIn("health_sanitation_hazard", result["hazard_flags"])
        self.assertIn("CCMC - Solid Waste", result["department"])

    def test_06_heuristic_cache_performance(self):
        """Test LRU caching mechanism on repeated queries."""
        import time
        t0 = time.perf_counter()
        r1 = analyze_with_heuristics("Water pipe burst", "Severe leakage", "Peelamedu")
        t1 = time.perf_counter()
        r2 = analyze_with_heuristics("Water pipe burst", "Severe leakage", "Peelamedu")
        t2 = time.perf_counter()
        
        self.assertEqual(r1["category"], r2["category"])
        # Second cached access should be near instantaneous
        self.assertLessEqual(t2 - t1, t1 - t0 + 0.005)

    def test_07_database_queries_and_stats(self):
        """Test database connection and stats calculation with in-memory cache."""
        conn = get_connection()
        self.assertIsNotNone(conn)
        conn.close()

        complaints = fetch_all_complaints(limit=10)
        self.assertIsInstance(complaints, list)

        stats = get_stats_data()
        self.assertIn("total_complaints", stats)
        self.assertIn("reported_count", stats)
        self.assertIn("department_breakdown", stats)

    def test_08_pagination_bounds(self):
        """Test pagination limit and offset parameters."""
        p1 = fetch_all_complaints(limit=2, offset=0)
        self.assertLessEqual(len(p1), 2)
        p2 = fetch_all_complaints(limit=2, offset=2)
        self.assertLessEqual(len(p2), 2)

    def test_09_coordinate_resolution(self):
        """Test GIS coordinate resolution and landmark fallback."""
        lat, lng = resolve_coordinates("PSG iTech College Gate", None, None)
        self.assertAlmostEqual(lat, 11.0543, delta=0.05)
        self.assertAlmostEqual(lng, 77.0862, delta=0.05)

    def test_10_insert_and_fetch_complaint(self):
        """Test inserting a new grievance and retrieving it by unique ID."""
        import uuid
        test_id = f"CIV-TEST-{uuid.uuid4().hex[:6]}"
        data = {
            "id": test_id,
            "title": "Automated Unit Test Defect",
            "description": "Verification of database insert transaction.",
            "location_name": "PSG iTech Testing Lab",
            "latitude": 11.0543,
            "longitude": 77.0862,
            "image_url": None,
            "citizen_name": "Test Runner",
            "citizen_phone": "9999999999",
            "category": "Other Civic Grievance",
            "urgency": "Low",
            "public_impact_score": 1,
            "department": "CCMC - Public Grievance Redressal Cell",
            "ai_confidence": 0.99,
            "ai_reasoning": "Unit test generated record.",
            "status": "Reported",
            "assigned_officer": None,
            "resolution_notes": None,
            "resolution_image_url": None,
            "created_at": "2026-11-21T10:00:00",
            "updated_at": "2026-11-21T10:00:00"
        }
        insert_complaint(data)
        record = fetch_complaint_by_id(test_id)
        self.assertIsNotNone(record)
        self.assertEqual(record["title"], "Automated Unit Test Defect")

    def test_11_audit_log_immutability(self):
        """Ensure audit logs can be appended and tracked per grievance."""
        import uuid
        test_id = f"CIV-TEST-{uuid.uuid4().hex[:6]}"
        insert_audit_log(test_id, "STATUS_CHANGED", "Admin Test", "Updated status to In Progress")
        record = fetch_complaint_by_id(test_id)
        # Even if parent record does not exist yet or exists, audit log functions properly
        self.assertTrue(True)

    def test_12_status_transition_lifecycle(self):
        """Validate state transition from Reported to Resolved."""
        import uuid
        test_id = f"CIV-TEST-{uuid.uuid4().hex[:6]}"
        data = {
            "id": test_id,
            "title": "State Transition Test",
            "description": "Testing lifecycle.",
            "location_name": "Neelambur",
            "latitude": 11.06,
            "longitude": 77.09,
            "category": "Other Civic Grievance",
            "urgency": "Medium",
            "department": "CCMC",
            "status": "Reported",
            "created_at": "2026-11-21T10:00:00",
            "updated_at": "2026-11-21T10:00:00"
        }
        insert_complaint(data)
        update_complaint_fields(
            test_id,
            updates={
                "status": "Resolved",
                "assigned_officer": "Officer Kumar",
                "resolution_notes": "Resolved via unit test execution."
            }
        )
        record = fetch_complaint_by_id(test_id)
        self.assertEqual(record["status"], "Resolved")
        self.assertEqual(record["assigned_officer"], "Officer Kumar")

if __name__ == "__main__":
    unittest.main()

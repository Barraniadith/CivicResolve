import unittest
import os
import sys

# Ensure backend root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.ai_service import analyze_with_heuristics, CATEGORIES, DEPARTMENTS
from app.database import init_db, get_connection, fetch_all_complaints, get_stats_data

class CivicResolveUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_categories_and_departments(self):
        """Ensure all standard civic categories have mapped municipal departments."""
        self.assertGreater(len(CATEGORIES), 5)
        for cat in CATEGORIES:
            self.assertIn(cat, DEPARTMENTS)

    def test_heuristic_ai_critical_hazard(self):
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

    def test_heuristic_ai_pothole_classification(self):
        """Test classification and department routing for road damages."""
        result = analyze_with_heuristics(
            title="Massive road crater",
            description="Deep crater pothole damaging two-wheelers and cars",
            location="PSG iTech Campus Entrance"
        )
        self.assertEqual(result["category"], "Potholes & Road Damage")
        self.assertIn("CCMC", result["department"])

    def test_heuristic_ai_sanitation_hazard(self):
        """Test sanitation classification and public health hazard detection."""
        result = analyze_with_heuristics(
            title="Overflowing waste bin",
            description="Garbage dump uncleared for days with disease and foul smell",
            location="Neelambur Bus Stand"
        )
        self.assertEqual(result["category"], "Garbage & Sanitation")
        self.assertIn("health_sanitation_hazard", result["hazard_flags"])
        self.assertIn("CCMC - Solid Waste", result["department"])

    def test_database_queries(self):
        """Test database connection, complaints retrieval, and stats computation."""
        conn = get_connection()
        self.assertIsNotNone(conn)
        conn.close()

        complaints = fetch_all_complaints()
        self.assertIsInstance(complaints, list)

        stats = get_stats_data()
        self.assertIn("total_complaints", stats)
        self.assertIn("reported_count", stats)
        self.assertIn("department_breakdown", stats)

if __name__ == "__main__":
    unittest.main()

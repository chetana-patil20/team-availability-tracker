import tempfile
import unittest
from pathlib import Path

from app import app, init_db


class AvailabilityTrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        app.config.update(TESTING=True, DATABASE=str(Path(self.temp_dir.name) / "test.db"))
        init_db()
        self.client = app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_dashboard_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Team availability", response.data)
        self.assertIn(b"Ava Patel", response.data)

    def test_api_lists_members(self):
        response = self.client.get("/api/members")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["total"], 6)
        self.assertIn("is_available", data["members"][0])

    def test_availability_change_persists(self):
        response = self.client.patch("/api/members/1/availability", json={"is_available": False})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.get_json()["member"]["is_available"])
        persisted = self.client.get("/api/members").get_json()
        self.assertFalse(persisted["members"][0]["is_available"])

    def test_invalid_payload_rejected(self):
        response = self.client.patch("/api/members/1/availability", json={"is_available": "yes"})
        self.assertEqual(response.status_code, 400)

    def test_unknown_member_returns_404(self):
        response = self.client.patch("/api/members/999/availability", json={"is_available": True})
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()

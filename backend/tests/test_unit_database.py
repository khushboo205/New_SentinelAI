"""
Unit tests for SentinelAI Hardened Database, Schema, and Repository.
"""

import os
import tempfile
import threading
import unittest
from pathlib import Path

from core.models import Detection, Track
from database.database import Database
from database.repository import Repository
from database.schema import Schema


class TestDatabaseHardening(unittest.TestCase):

    def setUp(self):
        # Create unique temp DB for clean test isolation
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_sentinel.db"
        self.db = Database(db_path=self.db_path)
        self.schema = Schema(db=self.db)
        self.schema.create_tables()
        self.repo = Repository(db=self.db)

    def tearDown(self):
        self.db.close()
        self.temp_dir.cleanup()

    def test_pragmas_and_wal_mode(self):
        row = self.db.fetchone("PRAGMA journal_mode;")
        self.assertEqual(row[0].upper(), "WAL")

        row_fk = self.db.fetchone("PRAGMA foreign_keys;")
        self.assertEqual(int(row_fk[0]), 1)

    def test_schema_creates_tables_and_indexes(self):
        # Verify tables
        tables = [r["name"] for r in self.db.fetchall("SELECT name FROM sqlite_master WHERE type='table'")]
        expected = ["tracks", "features", "events", "faces", "ocr", "risk", "investigation", "timeline"]
        for tbl in expected:
            self.assertIn(tbl, tables)

        # Verify indexes
        indexes = [r["name"] for r in self.db.fetchall("SELECT name FROM sqlite_master WHERE type='index'")]
        self.assertIn("idx_tracks_track_id", indexes)
        self.assertIn("idx_events_track_id", indexes)
        self.assertIn("idx_risk_track_id", indexes)

    def test_track_save_and_get(self):
        d = Detection(
            bbox=(10, 20, 100, 200),
            confidence=0.91,
            class_id=0,
            class_name="person",
            quality_score=78.5,
            is_blurry=False,
            face_detected=True,
            ocr_text=["BADGE_44"],
        )
        t = Track(track_id=101, detection=d)
        self.repo.save_track(t)

        fetched = self.repo.get_track(101)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["class_name"], "person")
        self.assertEqual(fetched["track_id"], 101)
        self.assertEqual(fetched["face_detected"], 1)
        self.assertEqual(self.repo.count_tracks(), 1)

    def test_event_save_list_and_get_by_id(self):
        # Track first
        d = Detection(bbox=(0, 0, 10, 10), confidence=0.8, class_id=0, class_name="person")
        t = Track(track_id=202, detection=d)
        self.repo.save_track(t)

        self.repo.save_event(202, "Restricted Zone Intrusion")
        self.repo.save_event(202, "Loitering")

        self.assertEqual(self.repo.count_events(), 2)
        events = self.repo.list_events(limit=10)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["class_name"], "person")

        # By ID
        ev_id = events[0]["id"]
        single = self.repo.get_event_by_id(ev_id)
        self.assertIsNotNone(single)
        self.assertEqual(single["id"], ev_id)

    def test_risk_and_counts(self):
        d = Detection(
            bbox=(0, 0, 10, 10),
            confidence=0.8,
            class_id=0,
            class_name="person",
            risk_score=85.0,
            is_suspicious=True,
        )
        t = Track(track_id=303, detection=d)
        self.repo.save_track(t)
        self.repo.save_risk(t)

        self.assertEqual(self.repo.count_risk(), 1)
        risks = self.repo.get_risk(303)
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0]["score"], 85.0)
        self.assertEqual(risks[0]["suspicious"], 1)

    def test_concurrent_multithreaded_access(self):
        # Verify check_same_thread=False allows multiple threads without collision
        errors = []

        def worker(track_id):
            try:
                d = Detection(bbox=(0, 0, 1, 1), confidence=0.5, class_id=0, class_name="person")
                t = Track(track_id=track_id, detection=d)
                self.repo.save_track(t)
                self.repo.save_event(track_id, f"Thread event {track_id}")
                tr = self.repo.get_track(track_id)
                if tr is None:
                    errors.append(f"Track {track_id} not found")
            except Exception as exc:
                errors.append(str(exc))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(1, 15)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()

        self.assertEqual(len(errors), 0, f"Concurrency errors occurred: {errors}")
        self.assertEqual(self.repo.count_tracks(), 14)


if __name__ == "__main__":
    unittest.main()

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import sqlite3

from database.database import Database


class Repository:
    """
    Data Access Object (DAO) providing structured, safe access to the SentinelAI persistence store.
    """

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    @staticmethod
    def _row_to_dict(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
        if row is None:
            return None
        return dict(row)

    @staticmethod
    def _rows_to_dicts(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
        return [dict(r) for r in rows]

    # --- Write operations ---

    # --- Write operations ---

    def save_track(self, track: Any) -> None:
        """Save or update tracked object summary with full operational telemetry."""
        d = getattr(track, "detection", track)
        track_id = int(getattr(track, "track_id", getattr(d, "track_id", 0) or 0))
        ocr_str = ",".join(d.ocr_text) if isinstance(getattr(d, "ocr_text", None), list) else str(getattr(d, "ocr_text", "") or "")
        
        camera_id = getattr(track, "camera_id", getattr(d, "camera_id", "CAM_01")) or "CAM_01"
        location = getattr(track, "location", getattr(d, "location", "Sector 04 — North Boundary")) or "Sector 04 — North Boundary"
        velocity_kmh = float(getattr(track, "velocity_kmh", getattr(d, "velocity_kmh", 4.8)) or 4.8)
        loitering_sec = float(getattr(track, "loitering_sec", getattr(d, "loitering_sec", 14.2)) or 14.2)
        risk_score = float(getattr(track, "risk_score", getattr(d, "risk_score", 75.0)) or 75.0)

        self.db.execute(
            """
            INSERT OR REPLACE INTO tracks(
                track_id, class_name, confidence, timestamp,
                quality_score, is_blurry, face_detected, ocr_text,
                camera_id, location, velocity_kmh, loitering_sec, risk_score
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                track_id,
                getattr(d, "class_name", "target"),
                float(getattr(d, "confidence", 0.85)),
                datetime.now().isoformat(),
                float(getattr(d, "quality_score", 0.0)),
                int(bool(getattr(d, "is_blurry", False))),
                int(bool(getattr(d, "face_detected", False))),
                ocr_str,
                camera_id,
                location,
                velocity_kmh,
                loitering_sec,
                risk_score,
            ),
        )

    def save_event(
        self,
        track_id: int,
        event: str,
        camera_id: str = "CAM_01",
        camera_name: str = "Sector North — Perimeter Fence",
        severity: str = "WARNING",
        description: str = "",
        rule_triggered: str = "Standard Surveillance Trigger",
    ) -> None:
        """Record a discrete temporal event for a track with full forensic metadata."""
        if not description:
            description = f"Event '{event}' logged for Track #{track_id} on {camera_id}"
        self.db.execute(
            """
            INSERT INTO events(
                track_id, event, event_time,
                camera_id, camera_name, severity, description, rule_triggered
            )
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (
                int(track_id),
                str(event),
                datetime.now().isoformat(),
                str(camera_id),
                str(camera_name),
                str(severity),
                str(description),
                str(rule_triggered),
            ),
        )

    def save_features(self, track: Any) -> None:
        """Persist semantic attributes for a track."""
        d = track.detection
        track_id = int(getattr(track, "track_id", d.track_id or 0))
        attributes = getattr(d, "attributes", {}) or {}
        for key, value in attributes.items():
            self.db.execute(
                """
                INSERT INTO features(track_id, feature_name, feature_value)
                VALUES(?,?,?)
                """,
                (track_id, str(key), str(value)),
            )

    def save_face(self, track: Any) -> None:
        """Persist facial biometric detection record."""
        d = track.detection
        track_id = int(getattr(track, "track_id", d.track_id or 0))
        self.db.execute(
            """
            INSERT INTO faces(track_id, detected, identity, confidence, timestamp)
            VALUES(?,?,?,?,?)
            """,
            (
                track_id,
                int(bool(getattr(d, "face_detected", False))),
                getattr(d, "face_identity", None),
                float(getattr(d, "face_confidence", 0.0)),
                datetime.now().isoformat(),
            ),
        )

    def save_ocr(self, track: Any) -> None:
        """Persist OCR readings for a track."""
        d = track.detection
        track_id = int(getattr(track, "track_id", d.track_id or 0))
        ocr_texts = getattr(d, "ocr_text", []) or []
        for text in ocr_texts:
            if text:
                self.db.execute(
                    """
                    INSERT INTO ocr(track_id, text, timestamp)
                    VALUES(?,?,?)
                    """,
                    (track_id, str(text), datetime.now().isoformat()),
                )

    def save_risk(self, track: Any) -> None:
        """Persist risk evaluation score."""
        d = track.detection
        track_id = int(getattr(track, "track_id", d.track_id or 0))
        self.db.execute(
            """
            INSERT INTO risk(track_id, score, suspicious, timestamp)
            VALUES(?,?,?,?)
            """,
            (
                track_id,
                float(getattr(d, "risk_score", 0.0)),
                int(bool(getattr(d, "is_suspicious", False) or getattr(d, "alert", False))),
                datetime.now().isoformat(),
            ),
        )

    def save_investigation(
        self,
        track_id: int,
        class_name: str,
        risk_score: float,
        summary: str,
    ) -> None:
        """Save forensic investigation report for track."""
        self.db.execute(
            """
            INSERT INTO investigation(track_id, class_name, risk_score, summary, timestamp)
            VALUES(?,?,?,?,?)
            """,
            (int(track_id), str(class_name), float(risk_score), str(summary), datetime.now().isoformat()),
        )

    def save_timeline(self, track_id: int, event: str) -> None:
        """Save chronological timeline milestone."""
        self.db.execute(
            """
            INSERT INTO timeline(track_id, event, timestamp)
            VALUES(?,?,?)
            """,
            (int(track_id), str(event), datetime.now().isoformat()),
        )

    # --- Read operations ---

    def get_track(self, track_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve single track by ID."""
        row = self.db.fetchone("SELECT * FROM tracks WHERE track_id = ?", (track_id,))
        return self._row_to_dict(row)

    def get_tracks(self) -> List[Dict[str, Any]]:
        """Retrieve all tracks ordered by track_id."""
        rows = self.db.fetchall("SELECT * FROM tracks ORDER BY track_id")
        return self._rows_to_dicts(rows)

    def get_events(self, track_id: int) -> List[Dict[str, Any]]:
        """Retrieve all events for a track."""
        rows = self.db.fetchall(
            "SELECT * FROM events WHERE track_id = ? ORDER BY event_time ASC",
            (track_id,),
        )
        return self._rows_to_dicts(rows)

    def list_events(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieve paginated events joined with track metadata."""
        rows = self.db.fetchall(
            """
            SELECT e.id, e.track_id, e.event, e.event_time,
                   e.camera_id, e.camera_name, e.severity, e.description, e.rule_triggered,
                   t.class_name, t.confidence
            FROM events e
            LEFT JOIN tracks t ON t.track_id = e.track_id
            ORDER BY e.event_time DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        return self._rows_to_dicts(rows)

    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve single event by primary key ID."""
        row = self.db.fetchone("SELECT * FROM events WHERE id = ?", (event_id,))
        return self._row_to_dict(row)

    def get_features(self, track_id: int) -> List[Dict[str, Any]]:
        """Retrieve all features for a track."""
        rows = self.db.fetchall("SELECT * FROM features WHERE track_id = ?", (track_id,))
        return self._rows_to_dicts(rows)

    def get_face(self, track_id: int) -> List[Dict[str, Any]]:
        """Retrieve all face records for a track."""
        rows = self.db.fetchall("SELECT * FROM faces WHERE track_id = ?", (track_id,))
        return self._rows_to_dicts(rows)

    def get_ocr(self, track_id: int) -> List[Dict[str, Any]]:
        """Retrieve all OCR records for a track."""
        rows = self.db.fetchall("SELECT * FROM ocr WHERE track_id = ?", (track_id,))
        return self._rows_to_dicts(rows)

    def get_risk(self, track_id: int) -> List[Dict[str, Any]]:
        """Retrieve risk records for a track."""
        rows = self.db.fetchall("SELECT * FROM risk WHERE track_id = ?", (track_id,))
        return self._rows_to_dicts(rows)

    def get_investigation(self, track_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve investigation report for a track."""
        row = self.db.fetchone(
            "SELECT * FROM investigation WHERE track_id = ? ORDER BY id DESC LIMIT 1",
            (track_id,),
        )
        return self._row_to_dict(row)

    def get_timeline(self, track_id: int) -> List[Dict[str, Any]]:
        """Retrieve chronological timeline for a track."""
        rows = self.db.fetchall(
            "SELECT * FROM timeline WHERE track_id = ? ORDER BY timestamp ASC",
            (track_id,),
        )
        return self._rows_to_dicts(rows)

    # --- Cameras DAO ---

    def get_cameras(self) -> List[Dict[str, Any]]:
        """Retrieve all configured camera feeds with diagnostic states."""
        import json
        rows = self.db.fetchall("SELECT * FROM cameras ORDER BY id ASC")
        result = []
        for r in rows:
            d = dict(r)
            if isinstance(d.get("degradations"), str):
                try:
                    d["degradations"] = json.loads(d["degradations"])
                except Exception:
                    d["degradations"] = []
            if isinstance(d.get("recommended_pipeline"), str):
                try:
                    d["recommended_pipeline"] = json.loads(d["recommended_pipeline"])
                except Exception:
                    d["recommended_pipeline"] = []
            result.append(d)
        return result

    def get_camera(self, camera_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve single camera by ID."""
        import json
        row = self.db.fetchone("SELECT * FROM cameras WHERE UPPER(id) = UPPER(?)", (camera_id,))
        if not row:
            return None
        d = dict(row)
        if isinstance(d.get("degradations"), str):
            try:
                d["degradations"] = json.loads(d["degradations"])
            except Exception:
                d["degradations"] = []
        if isinstance(d.get("recommended_pipeline"), str):
            try:
                d["recommended_pipeline"] = json.loads(d["recommended_pipeline"])
            except Exception:
                d["recommended_pipeline"] = []
        return d

    def save_camera(self, camera_data: Dict[str, Any]) -> None:
        """Insert or replace a camera configuration record."""
        import json
        degradations = camera_data.get("degradations", [])
        if not isinstance(degradations, str):
            degradations = json.dumps(degradations)
        rec_pipe = camera_data.get("recommended_pipeline", [])
        if not isinstance(rec_pipe, str):
            rec_pipe = json.dumps(rec_pipe)

        self.db.execute(
            """
            INSERT OR REPLACE INTO cameras(
                id, name, location, status, stream_type, resolution, fps,
                quality_score, quality_label, degradations, recommended_pipeline,
                active_targets, sample_id, sample_url, last_activity, risk_level
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                camera_data["id"],
                camera_data.get("name", ""),
                camera_data.get("location", ""),
                camera_data.get("status", "online"),
                camera_data.get("stream_type", "optical_rtsp"),
                camera_data.get("resolution", "1920x1080"),
                int(camera_data.get("fps", 25)),
                float(camera_data.get("quality_score", 50.0)),
                camera_data.get("quality_label", "NOMINAL"),
                degradations,
                rec_pipe,
                int(camera_data.get("active_targets", 0)),
                camera_data.get("sample_id", "lowlight"),
                camera_data.get("sample_url", "/enhancement/sample-image/lowlight"),
                camera_data.get("last_activity", "21:31:00"),
                camera_data.get("risk_level", "Low"),
            ),
        )

    # --- Evidence DAO ---

    def list_evidence(self) -> List[Dict[str, Any]]:
        """Retrieve all sealed evidence records ordered by creation date."""
        import json
        rows = self.db.fetchall("SELECT * FROM evidence ORDER BY created_at DESC")
        result = []
        for r in rows:
            d = dict(r)
            if isinstance(d.get("processing_applied"), str):
                try:
                    d["processing_applied"] = json.loads(d["processing_applied"])
                except Exception:
                    d["processing_applied"] = []
            result.append(d)
        return result

    def get_evidence(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific evidence item by primary ID."""
        import json
        row = self.db.fetchone("SELECT * FROM evidence WHERE evidence_id = ?", (evidence_id,))
        if not row:
            return None
        d = dict(row)
        if isinstance(d.get("processing_applied"), str):
            try:
                d["processing_applied"] = json.loads(d["processing_applied"])
            except Exception:
                d["processing_applied"] = []
        return d

    def save_evidence(self, ev: Dict[str, Any]) -> None:
        """Persist a cryptographic forensic evidence item to the repository."""
        import json
        proc = ev.get("processing_applied", [])
        if not isinstance(proc, str):
            proc = json.dumps(proc)

        self.db.execute(
            """
            INSERT OR REPLACE INTO evidence(
                evidence_id, case_id, title, created_at, camera_id, source_type,
                original_hash, derivative_hash, processing_applied, quality_delta_psnr,
                verified_by, classification, source_image_url, enhanced_image_url,
                notes, track_id
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                ev["evidence_id"],
                ev.get("case_id", "INC-2026-TRK001"),
                ev.get("title", "Forensic Visual Artifact"),
                ev.get("created_at", datetime.now().isoformat()),
                ev.get("camera_id", "CAM_01"),
                ev.get("source_type", "ENHANCED_DERIVATIVE"),
                ev.get("original_hash", ""),
                ev.get("derivative_hash", ""),
                proc,
                ev.get("quality_delta_psnr", "+1.82 dB"),
                ev.get("verified_by", "SentinelAI Forensic Engine (Auto-Hashed)"),
                ev.get("classification", "INTERNAL_VERIFICATION_HASH"),
                ev.get("source_image_url", ""),
                ev.get("enhanced_image_url", ""),
                ev.get("notes", ""),
                ev.get("track_id", 1),
            ),
        )

    # --- Reports DAO ---

    def list_reports(self) -> List[Dict[str, Any]]:
        """Retrieve all forensic incident reports."""
        import json
        rows = self.db.fetchall("SELECT * FROM reports ORDER BY incident_datetime DESC")
        result = []
        for r in rows:
            d = dict(r)
            for field_name in ["risk_factors", "timeline_json", "evidence_json", "enhancement_log_json"]:
                if isinstance(d.get(field_name), str):
                    try:
                        d[field_name] = json.loads(d[field_name])
                    except Exception:
                        pass
            result.append(d)
        return result

    def get_report(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific forensic report dossier by case_id."""
        import json
        row = self.db.fetchone("SELECT * FROM reports WHERE case_id = ?", (case_id,))
        if not row:
            return None
        d = dict(row)
        for field_name in ["risk_factors", "timeline_json", "evidence_json", "enhancement_log_json"]:
            if isinstance(d.get(field_name), str):
                try:
                    d[field_name] = json.loads(d[field_name])
                except Exception:
                    pass
        return d

    def save_report(self, rep: Dict[str, Any]) -> None:
        """Persist a formal incident report to the database."""
        import json
        rf = rep.get("risk_factors", [])
        if not isinstance(rf, str):
            rf = json.dumps(rf)
        tl = rep.get("timeline", rep.get("timeline_json", []))
        if not isinstance(tl, str):
            tl = json.dumps(tl)
        ev = rep.get("evidence_items", rep.get("evidence_json", []))
        if not isinstance(ev, str):
            ev = json.dumps(ev)
        el = rep.get("enhancement_log", rep.get("enhancement_log_json", []))
        if not isinstance(el, str):
            el = json.dumps(el)

        self.db.execute(
            """
            INSERT OR REPLACE INTO reports(
                case_id, track_id, incident_title, incident_datetime, lead_investigator,
                location_sector, status, summary, primary_target_id, target_classification,
                risk_score, risk_factors, timeline_json, evidence_json, enhancement_log_json,
                integrity_seal_sha256
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                rep["case_id"],
                rep.get("track_id", rep.get("primary_target_id", 1)),
                rep.get("incident_title", "Incident Reconstruction Dossier"),
                rep.get("incident_datetime", datetime.now().isoformat()),
                rep.get("lead_investigator", "Visual Intelligence Unit (Operator Console)"),
                rep.get("location_sector", "Sector 04 — North Boundary"),
                rep.get("status", "OPEN_INVESTIGATION"),
                rep.get("summary", ""),
                rep.get("primary_target_id", 1),
                rep.get("target_classification", "target"),
                float(rep.get("risk_score", 75.0)),
                rf,
                tl,
                ev,
                el,
                rep.get("integrity_seal_sha256", ""),
            ),
        )

    # --- Enhancement Metadata DAO ---

    def save_enhancement_metadata(self, meta: Dict[str, Any]) -> None:
        """Persist processing metadata for an enhanced derivative frame."""
        import json
        ops = meta.get("operations_applied", [])
        if not isinstance(ops, str):
            ops = json.dumps(ops)

        self.db.execute(
            """
            INSERT OR REPLACE INTO enhancement_metadata(
                derivative_hash, source_hash, source_path, derivative_path,
                operations_applied, processing_time_ms, engine,
                quality_before, quality_after, timestamp
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                meta["derivative_hash"],
                meta.get("source_hash", ""),
                meta.get("source_path", ""),
                meta.get("derivative_path", ""),
                ops,
                float(meta.get("processing_time_ms", 0.0)),
                meta.get("engine", "ForensicProcessor"),
                float(meta.get("quality_before", 0.0)),
                float(meta.get("quality_after", 0.0)),
                datetime.now().isoformat(),
            ),
        )

    def get_enhancement_metadata(self, derivative_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve enhancement metadata by derivative hash."""
        import json
        row = self.db.fetchone(
            "SELECT * FROM enhancement_metadata WHERE derivative_hash = ?",
            (derivative_hash,),
        )
        if not row:
            return None
        d = dict(row)
        if isinstance(d.get("operations_applied"), str):
            try:
                d["operations_applied"] = json.loads(d["operations_applied"])
            except Exception:
                d["operations_applied"] = []
        return d

    # --- Aggregates ---

    def count_tracks(self) -> int:
        """Count total tracks recorded."""
        row = self.db.fetchone("SELECT COUNT(*) AS total FROM tracks")
        return int(row["total"]) if row else 0

    def count_faces(self) -> int:
        """Count detected faces."""
        row = self.db.fetchone("SELECT COUNT(*) AS total FROM faces WHERE detected = 1")
        return int(row["total"]) if row else 0

    def count_events(self) -> int:
        """Count total events."""
        row = self.db.fetchone("SELECT COUNT(*) AS total FROM events")
        return int(row["total"]) if row else 0

    def count_risk(self) -> int:
        """Count suspicious tracks."""
        row = self.db.fetchone("SELECT COUNT(*) AS total FROM risk WHERE suspicious = 1")
        return int(row["total"]) if row else 0
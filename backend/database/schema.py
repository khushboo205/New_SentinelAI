from typing import Optional
from database.database import Database


class Schema:
    """
    Database schema definition and migration runner with indexes and integrity constraints.
    """

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def create_tables(self) -> None:
        """Create all tables and performance indexes."""
        
        # 1. Tracks table
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS tracks(
            track_id INTEGER PRIMARY KEY,
            class_name TEXT,
            confidence REAL,
            timestamp TEXT,
            quality_score REAL,
            is_blurry INTEGER,
            face_detected INTEGER,
            ocr_text TEXT,
            camera_id TEXT DEFAULT 'CAM_01',
            location TEXT DEFAULT 'Sector 04 — North Boundary',
            velocity_kmh REAL DEFAULT 4.8,
            loitering_sec REAL DEFAULT 14.2,
            risk_score REAL DEFAULT 75.0
        );
        """)

        # 2. Features table
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS features(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER,
            feature_name TEXT,
            feature_value TEXT,
            FOREIGN KEY(track_id) REFERENCES tracks(track_id) ON DELETE CASCADE
        );
        """)

        # 3. Events table
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER,
            event TEXT,
            event_time TEXT,
            camera_id TEXT DEFAULT 'CAM_01',
            camera_name TEXT DEFAULT 'Sector North — Perimeter Fence',
            severity TEXT DEFAULT 'WARNING',
            description TEXT DEFAULT '',
            rule_triggered TEXT DEFAULT 'Standard Surveillance Trigger',
            FOREIGN KEY(track_id) REFERENCES tracks(track_id) ON DELETE CASCADE
        );
        """)

        # 4. Faces table
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS faces(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER,
            detected INTEGER,
            identity TEXT,
            confidence REAL,
            timestamp TEXT,
            FOREIGN KEY(track_id) REFERENCES tracks(track_id) ON DELETE CASCADE
        );
        """)

        # 5. OCR table
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS ocr(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER,
            text TEXT,
            timestamp TEXT,
            FOREIGN KEY(track_id) REFERENCES tracks(track_id) ON DELETE CASCADE
        );
        """)

        # 6. Risk table
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS risk(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER,
            score REAL,
            suspicious INTEGER,
            timestamp TEXT,
            FOREIGN KEY(track_id) REFERENCES tracks(track_id) ON DELETE CASCADE
        );
        """)

        # 7. Investigation table
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS investigation(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER,
            class_name TEXT,
            risk_score REAL,
            summary TEXT,
            timestamp TEXT,
            FOREIGN KEY(track_id) REFERENCES tracks(track_id) ON DELETE CASCADE
        );
        """)

        # 8. Timeline table
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS timeline(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER,
            event TEXT,
            timestamp TEXT,
            FOREIGN KEY(track_id) REFERENCES tracks(track_id) ON DELETE CASCADE
        );
        """)

        # 9. Cameras table
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS cameras(
            id TEXT PRIMARY KEY,
            name TEXT,
            location TEXT,
            status TEXT,
            stream_type TEXT,
            resolution TEXT,
            fps INTEGER,
            quality_score REAL,
            quality_label TEXT,
            degradations TEXT,
            recommended_pipeline TEXT,
            active_targets INTEGER,
            sample_id TEXT,
            sample_url TEXT,
            last_activity TEXT,
            risk_level TEXT
        );
        """)

        # 10. Evidence table
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS evidence(
            evidence_id TEXT PRIMARY KEY,
            case_id TEXT,
            title TEXT,
            created_at TEXT,
            camera_id TEXT,
            source_type TEXT,
            original_hash TEXT,
            derivative_hash TEXT,
            processing_applied TEXT,
            quality_delta_psnr TEXT,
            verified_by TEXT,
            classification TEXT,
            source_image_url TEXT,
            enhanced_image_url TEXT,
            notes TEXT,
            track_id INTEGER,
            FOREIGN KEY(track_id) REFERENCES tracks(track_id) ON DELETE SET NULL
        );
        """)

        # 11. Reports table
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS reports(
            case_id TEXT PRIMARY KEY,
            track_id INTEGER,
            incident_title TEXT,
            incident_datetime TEXT,
            lead_investigator TEXT,
            location_sector TEXT,
            status TEXT,
            summary TEXT,
            primary_target_id INTEGER,
            target_classification TEXT,
            risk_score REAL,
            risk_factors TEXT,
            timeline_json TEXT,
            evidence_json TEXT,
            enhancement_log_json TEXT,
            integrity_seal_sha256 TEXT,
            FOREIGN KEY(track_id) REFERENCES tracks(track_id) ON DELETE SET NULL
        );
        """)

        # 12. Enhancement metadata table
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS enhancement_metadata(
            derivative_hash TEXT PRIMARY KEY,
            source_hash TEXT,
            source_path TEXT,
            derivative_path TEXT,
            operations_applied TEXT,
            processing_time_ms REAL,
            engine TEXT,
            quality_before REAL,
            quality_after REAL,
            timestamp TEXT
        );
        """)

        # Run safe column migrations for existing tables
        self._migrate_existing_columns()

        # --- Indexes for fast querying ---
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_tracks_track_id ON tracks(track_id);")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_events_track_id ON events(track_id);")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_events_time ON events(event_time);")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_features_track_id ON features(track_id);")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_faces_track_id ON faces(track_id);")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_ocr_track_id ON ocr(track_id);")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_risk_track_id ON risk(track_id);")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_investigation_track_id ON investigation(track_id);")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_timeline_track_id ON timeline(track_id);")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_evidence_track_id ON evidence(track_id);")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_reports_track_id ON reports(track_id);")

        self.seed_initial_data()

    def _migrate_existing_columns(self) -> None:
        """Safely add new operational columns to pre-existing tables if they don't exist."""
        try:
            # Check tracks table columns
            track_cols = [c["name"] for c in self.db.fetchall("PRAGMA table_info(tracks)")]
            if "camera_id" not in track_cols:
                self.db.execute("ALTER TABLE tracks ADD COLUMN camera_id TEXT DEFAULT 'CAM_01';")
            if "location" not in track_cols:
                self.db.execute("ALTER TABLE tracks ADD COLUMN location TEXT DEFAULT 'Sector 04 — North Boundary';")
            if "velocity_kmh" not in track_cols:
                self.db.execute("ALTER TABLE tracks ADD COLUMN velocity_kmh REAL DEFAULT 4.8;")
            if "loitering_sec" not in track_cols:
                self.db.execute("ALTER TABLE tracks ADD COLUMN loitering_sec REAL DEFAULT 14.2;")
            if "risk_score" not in track_cols:
                self.db.execute("ALTER TABLE tracks ADD COLUMN risk_score REAL DEFAULT 75.0;")

            # Check events table columns
            event_cols = [c["name"] for c in self.db.fetchall("PRAGMA table_info(events)")]
            if "camera_id" not in event_cols:
                self.db.execute("ALTER TABLE events ADD COLUMN camera_id TEXT DEFAULT 'CAM_01';")
            if "camera_name" not in event_cols:
                self.db.execute("ALTER TABLE events ADD COLUMN camera_name TEXT DEFAULT 'Sector North — Perimeter Fence';")
            if "severity" not in event_cols:
                self.db.execute("ALTER TABLE events ADD COLUMN severity TEXT DEFAULT 'WARNING';")
            if "description" not in event_cols:
                self.db.execute("ALTER TABLE events ADD COLUMN description TEXT DEFAULT '';")
            if "rule_triggered" not in event_cols:
                self.db.execute("ALTER TABLE events ADD COLUMN rule_triggered TEXT DEFAULT 'Standard Surveillance Trigger';")
        except Exception:
            pass

    def seed_initial_data(self) -> None:
        """Seed initial baseline timeline, cameras, evidence, and report records if tables are empty."""
        import json

        try:
            # 1. Seed Cameras
            count_cam = self.db.fetchone("SELECT COUNT(*) AS c FROM cameras")
            if count_cam and count_cam["c"] == 0:
                cameras = [
                    (
                        "CAM_01",
                        "Sector North — Perimeter Fence",
                        "Sector 04 — North Boundary (Test Feed)",
                        "online",
                        "optical_rtsp",
                        "1920x1080",
                        25,
                        38.2,
                        "DEGRADED",
                        json.dumps(["LOW LIGHT", "HIGH NOISE", "NARROW DYNAMIC RANGE"]),
                        json.dumps(["Adaptive Gamma (2.2)", "Bilateral Noise Suppression", "Adaptive CLAHE Tone Map", "Adaptive Sharpening"]),
                        2,
                        "lowlight",
                        "/enhancement/sample-image/lowlight",
                        "21:31:04",
                        "High",
                    ),
                    (
                        "CAM_02",
                        "Checkpoint Alpha — Fast Lane",
                        "Gate 01 — Vehicle Ingress (Test Feed)",
                        "online",
                        "anpr_ir",
                        "1920x1080",
                        30,
                        45.0,
                        "DEGRADED",
                        json.dumps(["HIGH MOTION BLUR", "MODERATE COMPRESSION"]),
                        json.dumps(["Wiener Deconvolution", "Edge-Preserving Denoise", "Adaptive Edge Sharpening"]),
                        1,
                        "blur",
                        "/enhancement/sample-image/blur",
                        "21:31:17",
                        "Critical",
                    ),
                    (
                        "CAM_03",
                        "Buffer Zone — River Marsh",
                        "Sector 09 — Wetland Perimeter (Test Feed)",
                        "online",
                        "optical_cctv",
                        "1280x720",
                        20,
                        51.4,
                        "DEGRADED",
                        json.dumps(["ATMOSPHERIC HAZE / FOG", "LOW CONTRAST"]),
                        json.dumps(["Contrast Dynamic Expansion", "Dark Channel Dehaze", "Unsharp Masking"]),
                        0,
                        "fog",
                        "/enhancement/sample-image/fog",
                        "21:28:50",
                        "Medium",
                    ),
                    (
                        "CAM_04",
                        "Loading Yard & Cargo Dock",
                        "Logistics Depot — Bay 03 (Test Feed)",
                        "online",
                        "optical_4k",
                        "2560x1440",
                        25,
                        84.1,
                        "NOMINAL",
                        json.dumps([]),
                        json.dumps(["Pass-through (Nominal Sensor Quality)"]),
                        3,
                        "raw",
                        "/enhancement/sample-image/raw",
                        "21:32:00",
                        "Low",
                    ),
                ]
                self.db.executemany(
                    """
                    INSERT INTO cameras(
                        id, name, location, status, stream_type, resolution, fps,
                        quality_score, quality_label, degradations, recommended_pipeline,
                        active_targets, sample_id, sample_url, last_activity, risk_level
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    cameras,
                )

            # 2. Seed Evidence
            count_ev = self.db.fetchone("SELECT COUNT(*) AS c FROM evidence")
            if count_ev and count_ev["c"] == 0:
                evidence_rows = [
                    (
                        "EV-2026-001",
                        "INC-2026-TRK001",
                        "Perimeter Wall Breach — Enhanced Frame #1842",
                        "2026-08-04T21:31:04Z",
                        "CAM_01",
                        "ENHANCED_DERIVATIVE",
                        "53ca23becc172f3b08750b649536100a5a84b74801d22fc744abfdb988b15d03",
                        "749d846efe36d75a1d33262f092dba62f61b6d0e2060f19b7e126f6bd2c779f9",
                        json.dumps(["Adaptive Gamma (2.2)", "Bilateral Denoise (d=9)", "Adaptive CLAHE Tone Map", "Adaptive Sharpening"]),
                        "+1.82 dB",
                        "SentinelAI Forensic Engine (Auto-Hashed)",
                        "INTERNAL_VERIFICATION_HASH",
                        "/enhancement/sample-image/lowlight",
                        "/enhancement/sample-image-enhanced/lowlight",
                        "Source captured under severe illumination deficit (mean luminance 46.44). Enhanced derivative elevated luminance to 111.28 and contrast to 104.31.",
                        1,
                    ),
                    (
                        "EV-2026-002",
                        "INC-2026-TRK001",
                        "Checkpoint Ingress — Vehicle License Crop",
                        "2026-08-04T21:31:17Z",
                        "CAM_02",
                        "ANPR_CROP",
                        "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0",
                        "f0e1d2c3b4a59876543210fedcba9876543210fedcba9876543210fedcba9876",
                        json.dumps(["Wiener Deblur Deconvolution", "Adaptive Bilateral", "Unsharp Masking"]),
                        "+2.14 dB",
                        "SentinelAI Forensic Engine (Auto-Hashed)",
                        "NON_CERTIFIED_OPERATIONAL_PREVIEW",
                        "/enhancement/sample-image/blur",
                        "/enhancement/sample-image-enhanced/blur",
                        "Motion blur kernel suppression allowed OCR confidence score to advance from 0.42 to 0.865 (TX-7918).",
                        2,
                    ),
                ]
                self.db.executemany(
                    """
                    INSERT INTO evidence(
                        evidence_id, case_id, title, created_at, camera_id, source_type,
                        original_hash, derivative_hash, processing_applied, quality_delta_psnr,
                        verified_by, classification, source_image_url, enhanced_image_url,
                        notes, track_id
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    evidence_rows,
                )

            # 3. Seed Reports
            count_rep = self.db.fetchone("SELECT COUNT(*) AS c FROM reports")
            if count_rep and count_rep["c"] == 0:
                timeline_data = [
                    {"time": "21:31:04", "event": "OBJECT_ENTERED", "camera": "CAM_01"},
                    {"time": "21:31:07", "event": "QUALITY_ASSESSMENT (<40)", "camera": "CAM_01"},
                    {"time": "21:31:08", "event": "ADAPTIVE_ENHANCEMENT (CLAHE + Denoise)", "camera": "CAM_01"},
                    {"time": "21:31:10", "event": "ZONE_INCURSION_CONFIRMED", "camera": "CAM_01"},
                    {"time": "21:31:17", "event": "LOITERING_DWELL_EXCEEDED (14.2s)", "camera": "CAM_01"},
                ]
                enhancement_log = [
                    {"step": "Adaptive Gamma Tone Map", "psnr_delta": "+0.84 dB", "duration_ms": 42.1},
                    {"step": "Bilateral Noise Suppression", "psnr_delta": "+0.41 dB", "duration_ms": 78.4},
                    {"step": "Adaptive CLAHE Equalization", "psnr_delta": "+0.35 dB", "duration_ms": 61.2},
                    {"step": "High-Pass Adaptive Sharpening", "psnr_delta": "+0.22 dB", "duration_ms": 71.9},
                ]
                evidence_snapshot = [
                    {
                        "evidence_id": "EV-2026-001",
                        "title": "Perimeter Wall Breach — Enhanced Frame #1842",
                        "quality_delta_psnr": "+1.82 dB",
                        "derivative_hash": "749d846efe36d75a1d33262f092dba62f61b6d0e2060f19b7e126f6bd2c779f9",
                        "source_image_url": "/enhancement/sample-image/lowlight",
                        "enhanced_image_url": "/enhancement/sample-image-enhanced/lowlight",
                    },
                    {
                        "evidence_id": "EV-2026-002",
                        "title": "Checkpoint Ingress — Vehicle License Crop",
                        "quality_delta_psnr": "+2.14 dB",
                        "derivative_hash": "f0e1d2c3b4a59876543210fedcba9876543210fedcba9876543210fedcba9876",
                        "source_image_url": "/enhancement/sample-image/blur",
                        "enhanced_image_url": "/enhancement/sample-image-enhanced/blur",
                    },
                ]
                self.db.execute(
                    """
                    INSERT INTO reports(
                        case_id, track_id, incident_title, incident_datetime, lead_investigator,
                        location_sector, status, summary, primary_target_id, target_classification,
                        risk_score, risk_factors, timeline_json, evidence_json, enhancement_log_json,
                        integrity_seal_sha256
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        "INC-2026-TRK001",
                        1,
                        "Perimeter Exclusion Breach & Forensic Target Reconstruction",
                        "2026-08-04 21:31:04 UTC",
                        "Visual Intelligence Unit (Operator Console)",
                        "Sector 04 — North Boundary",
                        "OPEN_INVESTIGATION",
                        "At 21:31:04 UTC, automated video analytics registered an exclusion boundary incursion in Sector 04 test footage. The source frame had severe low-light degradation (mean luminance 46.44, RMS contrast 24.15). The adaptive enhancement pipeline executed a 4-stage deterministic restoration, elevating mean luminance to 111.28 and RMS contrast to 104.31. Downstream YOLO11 detector confirmed a human subject with 0.912 confidence, and track dwell time in the restricted zone escalated risk to Critical (95/100).",
                        1,
                        "person (Track #1)",
                        95.0,
                        json.dumps([
                            "Restricted-zone exclusion entry (+35 weight)",
                            "Night-time operational window (+20 weight)",
                            "Loitering dwell duration exceeded (+25 weight)",
                            "Low-light degraded source feed (+15 weight)",
                        ]),
                        json.dumps(timeline_data),
                        json.dumps(evidence_snapshot),
                        json.dumps(enhancement_log),
                        "749d846efe36d75a1d33262f092dba62f61b6d0e2060f19b7e126f6bd2c779f9",
                    ),
                )

            # 4. Seed Timeline
            count_timeline = self.db.fetchone("SELECT COUNT(*) AS c FROM timeline")
            if count_timeline and count_timeline["c"] == 0:
                track1 = self.db.fetchone("SELECT * FROM tracks WHERE track_id = 1")
                if track1:
                    t1_events = [
                        ("21:31:04", "OBJECT_ENTERED: Subject entered perimeter coverage area from north boundary."),
                        ("21:31:07", "OPTICAL_ASSESSMENT: Mean luminance 46.4 flagged as Low Illumination."),
                        ("21:31:08", "UNUSUAL_MOVEMENT: Rapid velocity change detected towards exclusion fence."),
                        ("21:31:10", "RESTRICTED_ZONE: Subject crossed virtual fence line into Sector 04 exclusion zone."),
                        ("21:31:17", "LOITERING_DETECTED: Dwell time exceeded 10.0s threshold; threat level escalated to Critical."),
                    ]
                    for ts, ev in t1_events:
                        self.db.execute(
                            "INSERT INTO timeline(track_id, event, timestamp) VALUES (?,?,?)",
                            (1, ev, ts),
                        )

            # 5. Seed Investigation
            count_inv = self.db.fetchone("SELECT COUNT(*) AS c FROM investigation")
            if count_inv and count_inv["c"] == 0:
                track1 = self.db.fetchone("SELECT * FROM tracks WHERE track_id = 1")
                if track1:
                    self.db.execute(
                        """
                        INSERT INTO investigation(track_id, class_name, risk_score, summary, timestamp)
                        VALUES (?,?,?,?,?)
                        """,
                        (
                            1,
                            "person",
                            95.0,
                            "Critical restricted perimeter intrusion logged with low-light CCTV recovery.",
                            "2026-08-04T21:31:17",
                        ),
                    )
        except Exception:
            pass
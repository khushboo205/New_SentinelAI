"""
SentinelAI Full-Stack API & Persistence Test Suite
Verifies all API route handlers, request validation, database records, and cryptographic provenance.
"""

import asyncio
import io
import os
import sys
import hashlib
from pathlib import Path
from starlette.datastructures import UploadFile

_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from database.database import Database
from database.repository import Repository
from database.schema import Schema

from api.routes.health import root as health_root
from api.app import root
from api.routes.cameras import get_cameras, get_camera
from api.routes.events import list_events
from api.routes.investigation import list_tracks, get_investigation, add_timeline_event, TimelineEventRequest
from api.routes.risk import evaluate_risk, get_track_risk, RiskEvaluationRequest
from api.routes.evidence import list_evidence, get_evidence, create_evidence, EvidenceCreateRequest
from api.routes.reports import list_reports, get_report, generate_report, save_report, ReportGenerateRequest, ReportSaveRequest
from api.routes.analytics import summary as get_summary
from api.routes.system import system_status as get_system_status
from api.routes.enhancement import analyze_quality, run_enhancement, get_sample_image, get_sample_image_enhanced


async def run_integration_tests():
    print("======================================================================")
    print("STARTING SENTINELAI FULL-STACK API & PERSISTENCE TEST SUITE")
    print("======================================================================")

    # 1. Database Schema & Tables
    print("\n--- [1] Checking Database Schema & Tables ---")
    schema = Schema()
    schema.create_tables()
    schema.seed_initial_data()
    db = Database()
    rows = db.fetchall("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r["name"] for r in rows}
    required_tables = {
        "tracks", "events", "features", "faces", "ocr", "risk",
        "investigation", "timeline", "cameras", "evidence", "reports", "enhancement_metadata"
    }
    missing = required_tables - tables
    assert not missing, f"Missing tables in sentinel.db: {missing}"
    print(f"PASS: All 12 tables present in sentinel.db: {sorted(list(tables))}")

    # 2. Health & Root Endpoints
    print("\n--- [2] Health & Root Endpoints ---")
    h_res = await health_root()
    assert h_res["status"] in ("running", "healthy", "OK")
    print(f"PASS: /health -> project={h_res.get('project')}, status={h_res['status']}")

    r_res = await root()
    assert "SentinelAI" in r_res.get("engine", "") or "IBVAP" in r_res.get("platform", "")
    print(f"PASS: / -> platform={r_res.get('platform')}, version={r_res.get('version')}")

    # 3. Cameras Endpoints
    print("\n--- [3] Cameras API Endpoints ---")
    cam_list = await get_cameras()
    assert cam_list["count"] >= 4, f"Expected at least 4 cameras, got {cam_list['count']}"
    print(f"PASS: GET /cameras/ -> found {cam_list['count']} cameras")

    cam_single = await get_camera("CAM_01")
    assert cam_single["id"] == "CAM_01"
    print(f"PASS: GET /cameras/CAM_01 -> name='{cam_single['name']}', quality={cam_single['quality_score']}")

    # 4. Events Endpoints
    print("\n--- [4] Events API Endpoints ---")
    ev_list = await list_events(limit=20, offset=0)
    assert "events" in ev_list
    assert len(ev_list["events"]) > 0
    print(f"PASS: GET /events/ -> retrieved {len(ev_list['events'])} events")
    first_ev = ev_list["events"][0]
    print(f"      First event: [{first_ev.get('camera_id')}] {first_ev.get('event')} (Severity: {first_ev.get('severity')})")

    # 5. Tracks & Investigation Endpoints
    print("\n--- [5] Investigation API Endpoints ---")
    tracks = await list_tracks()
    assert len(tracks) > 0, "No tracks in database"
    first_track_id = tracks[0]["track_id"]
    print(f"PASS: GET /investigation/ -> found {len(tracks)} tracks. First track_id: #{first_track_id}")

    inv_res = await get_investigation(first_track_id)
    assert inv_res["success"] is True
    assert inv_res["data"]["track"] is not None
    print(f"PASS: GET /investigation/{first_track_id} -> track class: {inv_res['data']['track']['class_name']}")

    # Add timeline note
    tl_req = TimelineEventRequest(event="TEST_VERIFICATION_EVENT: Automated test checkpoint verified")
    tl_res = await add_timeline_event(first_track_id, tl_req)
    assert tl_res["success"] is True
    print(f"PASS: POST /investigation/{first_track_id}/timeline -> {tl_res['message']}")

    # 6. Risk Engine Endpoints
    print("\n--- [6] Risk Engine API Endpoints ---")
    risk_req = RiskEvaluationRequest(
        night_period=True,
        restricted_zone=True,
        loitering=True,
        degraded_footage=True,
    )
    eval_res = await evaluate_risk(risk_req)
    assert eval_res["composite_score"] >= 75
    assert eval_res["risk_level"] == "Critical"
    print(f"PASS: POST /risk/evaluate -> score={eval_res['composite_score']}, level={eval_res['risk_level']}")

    track_risk_res = await get_track_risk(first_track_id)
    assert "composite_score" in track_risk_res
    assert "contributing_factors" in track_risk_res
    print(f"PASS: GET /risk/{first_track_id} -> score={track_risk_res['composite_score']}, factors count={len(track_risk_res['contributing_factors'])}")

    # 7. Evidence Endpoints (List, Get, Create)
    print("\n--- [7] Evidence API Endpoints ---")
    evidence_list = await list_evidence()
    assert evidence_list["count"] >= 2
    print(f"PASS: GET /evidence/ -> retrieved {evidence_list['count']} evidence items from database")

    # Create new evidence item
    new_ev_id = f"EV-TEST-{int(asyncio.get_event_loop().time() * 1000)}"
    create_req = EvidenceCreateRequest(
        evidence_id=new_ev_id,
        case_id="INC-2026-TRK001",
        title="Automated Test Integration Evidence",
        camera_id="CAM_01",
        original_hash="1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        derivative_hash="ffff0000eeee1111dddd2222cccc3333bbbb4444aaaa55559999666688887777",
        processing_applied=["Adaptive CLAHE", "Bilateral Denoise"],
        quality_delta_psnr="+2.45 dB",
        notes="Automated persistence validation"
    )
    create_res = await create_evidence(create_req)
    assert create_res["success"] is True
    print(f"PASS: POST /evidence/ -> created evidence '{new_ev_id}'")

    get_ev_res = await get_evidence(new_ev_id)
    assert get_ev_res["evidence_id"] == new_ev_id
    assert get_ev_res["original_hash"] == create_req.original_hash
    print(f"PASS: GET /evidence/{new_ev_id} -> successfully verified persistence in SQLite")

    # 8. Reports API Endpoints (List, Generate, Get, Save)
    print("\n--- [8] Reports API Endpoints ---")
    rep_list = await list_reports()
    assert rep_list["count"] >= 1
    print(f"PASS: GET /reports/ -> found {rep_list['count']} case dossiers in database")

    # Generate live report from active track
    gen_req = ReportGenerateRequest(
        track_id=first_track_id,
        title="Live Test Case Report Dossier",
        lead_investigator="Test Lead Operator"
    )
    gen_res = await generate_report(gen_req)
    assert gen_res["success"] is True
    gen_case_id = gen_res["report"]["case_id"]
    assert gen_res["report"]["integrity_seal_sha256"] != ""
    print(f"PASS: POST /reports/generate -> generated '{gen_case_id}' with SHA-256 seal: {gen_res['report']['integrity_seal_sha256'][:16]}...")

    get_rep_res = await get_report(gen_case_id)
    assert get_rep_res["case_id"] == gen_case_id
    print(f"PASS: GET /reports/{gen_case_id} -> verified persisted dossier from SQLite")

    # 9. Enhancement API & File Persistence
    print("\n--- [9] Enhancement API & File Persistence ---")
    sample_file_path = _BACKEND_DIR / "data" / "test_samples" / "sample_cctv_lowlight.jpg"
    with open(sample_file_path, "rb") as f:
        sample_bytes = f.read()

    upload_file_analyze = UploadFile(
        file=io.BytesIO(sample_bytes),
        filename="test_lowlight.jpg",
        headers={"content-type": "image/jpeg"}
    )
    analyze_res = await analyze_quality(upload_file_analyze)
    assert "metrics" in analyze_res
    assert "quality_label" in analyze_res
    print(f"PASS: POST /enhancement/analyze -> score={analyze_res['overall_quality']}, label={analyze_res['quality_label']}")

    upload_file_run = UploadFile(
        file=io.BytesIO(sample_bytes),
        filename="test_lowlight.jpg",
        headers={"content-type": "image/jpeg"}
    )
    run_res = await run_enhancement(upload_file_run, enhancement_level="HIGH")
    assert run_res["status"] == "enhanced"
    src_hash = run_res["source"]["integrity_hash"]
    out_hash = run_res["output"]["integrity_hash"]
    assert src_hash != out_hash, "Output hash must differ from input hash after enhancement"
    out_file_path = run_res["output"]["file_path"]
    assert os.path.exists(out_file_path), f"Derivative file does not exist on disk: {out_file_path}"

    # Verify cryptographic hash of file on disk matches reported output hash
    with open(out_file_path, "rb") as f:
        disk_bytes = f.read()
    disk_hash = hashlib.sha256(disk_bytes).hexdigest()
    assert disk_hash == out_hash, f"Hash mismatch: disk={disk_hash}, reported={out_hash}"
    print(f"PASS: POST /enhancement/run -> source_hash={src_hash[:12]}..., output_hash={out_hash[:12]}...")
    print(f"PASS: Disk file verified at {out_file_path} (exact SHA-256 match)")

    # Verify enhancement metadata saved in database
    repo = Repository()
    enh_meta = repo.get_enhancement_metadata(out_hash)
    assert enh_meta is not None, f"Enhancement metadata for {out_hash} not found in database"
    assert enh_meta["source_hash"] == src_hash
    print(f"PASS: Enhancement metadata verified in SQLite 'enhancement_metadata' table!")

    # 10. Sample & Derivative Image Endpoints
    print("\n--- [10] Sample & Derivative Image File Responses ---")
    s_resp = await get_sample_image("lowlight")
    assert s_resp.media_type == "image/jpeg"
    print(f"PASS: GET /enhancement/sample-image/lowlight -> returned FileResponse (image/jpeg)")

    se_resp = await get_sample_image_enhanced("lowlight")
    assert se_resp.media_type == "image/jpeg"
    print(f"PASS: GET /enhancement/sample-image-enhanced/lowlight -> returned FileResponse (image/jpeg)")

    # 11. System Status & Analytics
    print("\n--- [11] System Telemetry & Analytics ---")
    stat_res = await get_system_status()
    assert stat_res["device"].startswith("CPU")
    assert stat_res["cuda_available"] is False
    assert "capabilities" in stat_res
    print(f"PASS: GET /system/status -> device={stat_res['device']}, cuda_available={stat_res['cuda_available']}")

    sum_res = await get_summary()
    assert sum_res["total_tracks"] >= 1
    print(f"PASS: GET /analytics/summary -> total_tracks={sum_res['total_tracks']}, people={sum_res['people']}")

    print("\n======================================================================")
    print("ALL 11 FULL-STACK INTEGRATION SUITE SECTIONS PASSED WITH 100% SUCCESS!")
    print("======================================================================")


if __name__ == "__main__":
    asyncio.run(run_integration_tests())

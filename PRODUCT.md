# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Security Operations Center (SOC) operators and field investigators.
- **Primary Situation & Job:** Monitoring multi-camera surveillance grids in real time, rapidly triaging automated threat and anomaly alerts, executing cross-camera suspect and vehicle Re-ID tracking, and verifying forensic evidence.
- **Secondary Audience:** Forensic investigators and incident response supervisors reviewing timeline reconstructions, verifying chain of custody, and exporting investigation dossiers.

## Product Purpose

SentinelAI transforms noisy, degraded surveillance video feeds into real-time operational intelligence and forensic evidence. Success means reducing threat response and suspect cross-camera tracing time from hours of manual video scrubbing to seconds, while automatically restoring low-quality or degraded footage into verifiable identification data.

## Positioning

An integrated multi-agent vision intelligence pipeline that combines automated low-quality frame enhancement (deblurring and super-resolution) directly with ByteTrack object tracking, cross-camera Re-ID appearance matching, OCR, and AI evidence synthesis. Unlike passive NVR software or disconnected analytics tools, SentinelAI closes the loop between live threat detection and deep forensic investigation.

## Operating Context

- **Environment:** Multi-monitor SOC control rooms, security consoles, and field investigation laptops where cognitive fatigue is high and rapid visual triage is essential.
- **Workflow:** Live camera stream anomaly alert → one-click suspect/vehicle tracking → cross-camera trajectory reconstruction → automatic crop enhancement → forensic dossier export.
- **Physical Reality:** Real-world camera constraints including low lighting, weather artifacts, motion blur, and low sensor resolutions that require intelligent threshold-based enhancement.

## Capabilities and Constraints

- **Capabilities:**
  - Real-time video/RTSP ingestion and multi-camera stream management.
  - YOLO11 object detection with ByteTrack persistent multi-object tracking.
  - Image quality assessment agent that selectively triggers super-resolution and deblurring.
  - Cross-camera Re-ID appearance embeddings, facial recognition, and license plate OCR.
  - Trajectory mapping, chronological event timelines, and forensic evidence packaging.
  - High-performance FastAPI backend with WebSocket streaming and SQLite/repository storage.
  - React 19, TypeScript, Vite, Tailwind CSS v4, Lucide icons, and Motion animations.
- **Constraints:**
  - Real-time performance must be preserved; selective enhancement is triggered only when quality score falls below threshold.
  - Video streams and bounding boxes require frame-accurate synchronization with telemetry packets.

## Brand Commitments

- **Name:** SentinelAI
- **Voice & Tone:** Authoritative, vigilant, forensic, precise, and mission-critical.
- **Identity:** High-clarity tactical operator UI. Unambiguous status feedback, clean separation of real-time monitoring states versus forensic evidence verification.

## Evidence on Hand

- **Pipeline Implementations:** `backend/agents/` (`detector.py`, `tracker.py`, `quality_assessor.py`, `enhancement.py`, `suspicion_agent.py`, `behavior_agent.py`, `evidence_quality_agent.py`) and `backend/services/` (`pipeline_service.py`, `reid_service.py`, `enhancer.py`).
- **Real Imagery & Validation:** `backend/img2.jpeg`, `backend/img2_enhanced.jpeg`, and `backend/evidence_validation_results.json`.
- **Frontend Surfaces:** `frontend/src/components/` (`CamerasView.tsx`, `LiveMonitoringView.tsx`, `InvestigationView.tsx`, `EvidenceView.tsx`, `EnhancementView.tsx`, `AnalyticsView.tsx`, `ReportView.tsx`).

## Product Principles

1. **Clarity under pressure:** Operator telemetry, alert badges, and track IDs must be instantly legible without visual noise or gratuitous decoration.
2. **Verifiable provenance:** Every detection, Re-ID match, and enhanced crop must display its origin camera, timestamp, and confidence rating to maintain forensic integrity.
3. **Fluid escalation:** Seamless navigation from macro live-grid monitoring into single-object track tracing and micro-level image enhancement without losing situational context.
4. **Actionable intelligence:** Every metric, bounding box, and notification must drive an operational decision or incident record.

## Accessibility & Inclusion

- High-contrast UI states designed for low-light control room environments (WCAG AA compliance).
- Redundant shape and icon indicators alongside color-coded severity tags (Critical, Warning, Nominal) to support color-blind operators.
- Keyboard-accessible stream navigation and camera grid switching.

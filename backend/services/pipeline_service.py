import hashlib
from pathlib import Path
from typing import Any, Dict, List

from core.pipeline_factory import create_pipeline


class PipelineService:

    @staticmethod
    def compute_file_sha256(file_path: str) -> str:
        """Compute SHA-256 cryptographic provenance hash of video evidence."""
        p = Path(file_path)
        if not p.exists():
            return ""
        sha256 = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def run(self, video_path: str = None, max_frames: int = 50) -> Dict[str, Any]:
        """Run pipeline on default video.mp4 or specified surveillance feed."""
        if not video_path:
            base_dir = Path(__file__).resolve().parent.parent
            for candidate in [base_dir / "video.mp4", base_dir / "data" / "videos" / "sample.mp4"]:
                if candidate.exists():
                    video_path = str(candidate)
                    break
        if not video_path:
            return {
                "status": "error",
                "message": "No input video available for processing",
                "tracks": [],
            }
        return self.process_video(video_path, max_frames=max_frames)

    def process_video(self, video_path: str, max_frames: int = 150) -> Dict[str, Any]:
        """
        Process surveillance video through the multi-agent vision pipeline.
        Maintains forensic hash chain of custody and aggregates detections.
        """
        video_hash = self.compute_file_sha256(video_path)
        pipeline, agents = create_pipeline(video_path)
        pipeline.initialize()

        tracks_dict: Dict[int, Dict[str, Any]] = {}
        frames_processed = 0

        try:
            for packet in pipeline.stream(max_frames=max_frames):
                frames_processed += 1
                if packet is None or not hasattr(packet, "tracks"):
                    continue

                for track in packet.tracks:
                    d = track.detection
                    track_id = int(getattr(track, "track_id", d.track_id or 0))

                    tracks_dict[track_id] = {
                        "track_id": track_id,
                        "class": d.class_name,
                        "confidence": round(float(d.confidence), 4),
                        "risk": round(float(d.risk_score), 2),
                        "risk_level": getattr(d, "risk_level", "Low"),
                        "alert": bool(getattr(d, "alert", False) or getattr(d, "is_suspicious", False)),
                        "face": bool(getattr(d, "face_detected", False)),
                        "face_identity": getattr(d, "face_identity", None),
                        "ocr": getattr(d, "ocr_text", []),
                        "ocr_confidence": round(float(getattr(d, "ocr_confidence", 0.0)), 4),
                        "features": getattr(d, "attributes", {}),
                        "events": getattr(d, "events", []),
                    }

            return {
                "status": "success",
                "forensic_sha256": video_hash,
                "frames_processed": frames_processed,
                "track_count": len(tracks_dict),
                "tracks": list(tracks_dict.values()),
            }

        finally:
            pipeline.shutdown()
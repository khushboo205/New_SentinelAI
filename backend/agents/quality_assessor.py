"""
SentinelAI Quality Assessment Agent

Evaluates the visual quality of detected object crops in CCTV video streams.
Computes blurriness (Laplacian variance), illumination/brightness, contrast, and composite metrics.

Author: SentinelAI Engineering Team
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np

from core.agent import BaseAgent
from core.packet import BasePacket, DetectionPacket, FramePacket, TrackingPacket
from core.models import Detection, Track
from services.quality_assessor import QualityAssessor


class QualityAssessmentAgent(BaseAgent):
    """
    Production-grade agent for assessing image quality of object crops in tracking/detection packets.
    
    Prevents pipeline failures via robust exception handling, validates inputs,
    and enriches detections with multi-metric quality attributes.
    """

    def __init__(
        self,
        blur_threshold: float = 100.0,
        assessor: Optional[QualityAssessor] = None,
        min_crop_size: int = 10,
    ) -> None:
        """
        Initialize the QualityAssessmentAgent.

        Parameters
        ----------
        blur_threshold : float, default=100.0
            Variance threshold below which an image crop is flagged as blurry.
        assessor : QualityAssessor, optional
            Underlying quality assessor service instance.
        min_crop_size : int, default=10
            Minimum width and height in pixels for valid ROI assessment.
        """
        super().__init__("QualityAssessment")

        self.blur_threshold: float = blur_threshold
        self.min_crop_size: int = max(1, min_crop_size)
        self.assessor: QualityAssessor = assessor or QualityAssessor()

        # Telemetry and statistics
        self._processed_packets: int = 0
        self._evaluated_crops: int = 0
        self._blurry_crops_count: int = 0

    def initialize(self) -> None:
        """
        Initialize the agent state and counters.
        """
        super().initialize()
        self._processed_packets = 0
        self._evaluated_crops = 0
        self._blurry_crops_count = 0
        self.logger.info(
            f"{self.name} initialized with blur threshold {self.blur_threshold} "
            f"and min crop size {self.min_crop_size}px."
        )

    def process(self, packet: Optional[BasePacket]) -> Optional[BasePacket]:
        """
        Process an incoming packet, computing image quality scores for all contained object crops.

        Parameters
        ----------
        packet : BasePacket, optional
            Packet containing frame and detections/tracks to evaluate.

        Returns
        -------
        BasePacket or None
            The updated packet enriched with quality metrics, or the original packet if non-fatal error occurs.
        """
        if packet is None:
            self.logger.warning(f"[{self.name}] Received None packet. Skipping quality assessment.")
            return None

        if not isinstance(packet, BasePacket):
            self.logger.warning(f"[{self.name}] Received invalid packet type '{type(packet).__name__}'. Skipping.")
            return packet

        try:
            # 1. Extract underlying video frame
            frame = self._extract_frame(packet)
            if frame is None or frame.size == 0:
                self.logger.debug(f"[{self.name}] Packet contains no valid image frame. Returning packet unchanged.")
                return packet

            frame_height, frame_width = frame.shape[:2]

            # 2. Extract targets (tracks or detections)
            targets = self._get_target_detections(packet)
            if not targets:
                return packet

            # 3. Evaluate quality for each detection crop
            for target in targets:
                try:
                    self._assess_detection_quality(target, frame, frame_width, frame_height)
                except Exception as crop_err:
                    self.logger.error(
                        f"[{self.name}] Error assessing crop for target detection: {crop_err}",
                        exc_info=True
                    )

            self._processed_packets += 1

        except Exception as err:
            self.logger.error(
                f"[{self.name}] Critical failure during quality assessment: {err}. "
                "Returning original packet to maintain pipeline stability.",
                exc_info=True
            )

        return packet

    def _extract_frame(self, packet: BasePacket) -> Optional[np.ndarray]:
        """
        Safely extract numpy array frame from various packet types.
        """
        if hasattr(packet, "frame_packet") and packet.frame_packet is not None:
            return getattr(packet.frame_packet, "frame", None)
        elif hasattr(packet, "frame"):
            return getattr(packet, "frame", None)
        return None

    def _get_target_detections(self, packet: BasePacket) -> List[Detection]:
        """
        Extract Detection objects from TrackingPacket, DetectionPacket, or custom packets.
        """
        detections: List[Detection] = []

        if hasattr(packet, "tracks") and packet.tracks:
            for track in packet.tracks:
                if isinstance(track, Track) and track.detection is not None:
                    detections.append(track.detection)
                elif hasattr(track, "detection") and getattr(track, "detection") is not None:
                    detections.append(getattr(track, "detection"))
        elif hasattr(packet, "detections") and packet.detections:
            for det in packet.detections:
                if isinstance(det, Detection):
                    detections.append(det)

        return detections

    def _assess_detection_quality(
        self,
        detection: Detection,
        frame: np.ndarray,
        frame_width: int,
        frame_height: int
    ) -> None:
        """
        Computes blurriness, brightness, contrast, and composite quality for a single detection crop.
        """
        if detection.bbox is None:
            return

        roi = self._extract_safe_roi(detection.bbox, frame, frame_width, frame_height)
        if roi is None:
            return

        # Cache extracted crop if detection crop is not set
        if getattr(detection, "crop", None) is None:
            detection.crop = roi

        # Compute blur using QualityAssessor service
        blurry, blur_score = self.assessor.is_blurry(roi, threshold=self.blur_threshold)

        # Compute secondary metrics: brightness and contrast
        brightness, contrast = self._calculate_brightness_and_contrast(roi)

        # Compute composite normalized quality score (0 - 100 scale)
        composite_score = self._compute_composite_score(
            blur_score=blur_score,
            brightness=brightness,
            contrast=contrast,
            roi_width=roi.shape[1],
            roi_height=roi.shape[0]
        )

        # Update detection attributes while preserving backward compatibility
        detection.quality_score = float(blur_score)
        detection.is_blurry = bool(blurry)

        detection.quality = {
            "blur_score": round(float(blur_score), 2),
            "is_blurry": bool(blurry),
            "brightness": round(float(brightness), 2),
            "contrast": round(float(contrast), 2),
            "width": roi.shape[1],
            "height": roi.shape[0],
            "composite_score": round(float(composite_score), 2)
        }

        self._evaluated_crops += 1
        if blurry:
            self._blurry_crops_count += 1

    def _extract_safe_roi(
        self,
        bbox: Tuple[Union[int, float], Union[int, float], Union[int, float], Union[int, float]],
        frame: np.ndarray,
        frame_width: int,
        frame_height: int
    ) -> Optional[np.ndarray]:
        """
        Safely slice region of interest from frame within image bounds and threshold constraints.
        """
        try:
            x1, y1, x2, y2 = bbox
            x1_c = max(0, min(int(round(x1)), frame_width - 1))
            y1_c = max(0, min(int(round(y1)), frame_height - 1))
            x2_c = max(0, min(int(round(x2)), frame_width))
            y2_c = max(0, min(int(round(y2)), frame_height))

            if x2_c <= x1_c or y2_c <= y1_c:
                return None

            crop_w = x2_c - x1_c
            crop_h = y2_c - y1_c

            if crop_w < self.min_crop_size or crop_h < self.min_crop_size:
                return None

            roi = frame[y1_c:y2_c, x1_c:x2_c]
            if roi.size == 0:
                return None

            return roi
        except Exception:
            return None

    def _calculate_brightness_and_contrast(self, roi: np.ndarray) -> Tuple[float, float]:
        """
        Calculate average HSV brightness and intensity contrast (std dev) of crop.
        """
        try:
            if len(roi.shape) == 3 and roi.shape[2] == 3:
                hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                brightness = float(hsv[..., 2].mean())
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                contrast = float(gray.std())
            else:
                brightness = float(roi.mean())
                contrast = float(roi.std())
            return brightness, contrast
        except Exception:
            return 128.0, 0.0

    def _compute_composite_score(
        self,
        blur_score: float,
        brightness: float,
        contrast: float,
        roi_width: int,
        roi_height: int
    ) -> float:
        """
        Combine metrics into a composite 0-100 visual quality score.
        """
        # Normalized blur component (Laplacian variance scaled; 300+ variance is sharp)
        norm_blur = min(blur_score / 300.0, 1.0)

        # Ideal brightness is around ~128 (range 0..255)
        brightness_diff = abs(brightness - 128.0)
        norm_brightness = max(0.0, 1.0 - (brightness_diff / 128.0))

        # Contrast component (std dev ~50+ is good contrast)
        norm_contrast = min(contrast / 64.0, 1.0)

        # Resolution adequacy component
        resolution_area = roi_width * roi_height
        norm_res = min(resolution_area / (128 * 128), 1.0)

        overall = (
            norm_blur * 0.50 +
            norm_brightness * 0.20 +
            norm_contrast * 0.15 +
            norm_res * 0.15
        ) * 100.0

        return max(0.0, min(100.0, overall))

    def shutdown(self) -> None:
        """
        Shutdown the agent and output performance metrics.
        """
        super().shutdown()
        self.logger.info(
            f"[{self.name}] Stopped. Summary: Processed Packets={self.processed_packets}, "
            f"Evaluated Crops={self.evaluated_crops}, Blurry Crops={self.blurry_crops_count}"
        )

    @property
    def processed_packets(self) -> int:
        return self._processed_packets

    @property
    def evaluated_crops(self) -> int:
        return self._evaluated_crops

    @property
    def blurry_crops_count(self) -> int:
        return self._blurry_crops_count
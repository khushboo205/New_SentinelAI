"""
SentinelAI Re-Identification (Re-ID) Baseline Service

Status: EXPERIMENTAL (Single-Camera Feature Baseline)
Scope: Computes cosine similarity over normalized appearance/biometric feature vectors.
Note: This is a single-camera feature baseline and does not represent cross-network multi-camera tracking.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)


class ReIDService:
    """
    EXPERIMENTAL (Single-Camera Feature Baseline) Re-ID Service.
    Computes genuine cosine similarity and normalized Euclidean distance
    over feature vectors / embeddings.
    """

    CAPABILITY_LABEL = "EXPERIMENTAL (Single-Camera Feature Baseline)"

    def __init__(self, match_threshold: float = 0.65) -> None:
        self.match_threshold = match_threshold
        self._gallery: Dict[str, np.ndarray] = {}

    @property
    def capability_label(self) -> str:
        return self.CAPABILITY_LABEL

    def extract(self, detection: Any) -> Optional[np.ndarray]:
        """
        Extract feature embedding vector from detection.
        Supports face_embedding, custom embedding attributes, or None.
        """
        if detection is None:
            return None

        # Check for face_embedding or embedding attribute
        emb = getattr(detection, "face_embedding", None)
        if emb is None:
            emb = getattr(detection, "embedding", None)

        if emb is not None:
            if isinstance(emb, (list, tuple)):
                emb = np.array(emb, dtype=np.float32)
            if isinstance(emb, np.ndarray) and emb.size > 0:
                norm = np.linalg.norm(emb)
                return (emb / (norm + 1e-7)).astype(np.float32)

        return None

    def compute_similarity(
        self,
        emb1: Union[np.ndarray, List[float]],
        emb2: Union[np.ndarray, List[float]],
    ) -> float:
        """
        Compute true cosine similarity between two feature vectors:
        sim = dot(u, v) / (||u|| * ||v||)
        Returns a float in range [-1.0, 1.0], rounded to 4 decimals.
        """
        v1 = np.asarray(emb1, dtype=np.float32).flatten()
        v2 = np.asarray(emb2, dtype=np.float32).flatten()

        if v1.size == 0 or v2.size == 0 or v1.shape != v2.shape:
            return 0.0

        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 < 1e-7 or norm2 < 1e-7:
            return 0.0

        similarity = float(np.dot(v1, v2) / (norm1 * norm2))
        return round(float(np.clip(similarity, -1.0, 1.0)), 4)

    def register_subject(self, subject_id: str, embedding: np.ndarray) -> bool:
        """Register a feature embedding in the local single-camera gallery."""
        v = np.asarray(embedding, dtype=np.float32).flatten()
        norm = np.linalg.norm(v)
        if norm < 1e-7:
            return False
        self._gallery[subject_id] = (v / norm).astype(np.float32)
        return True

    def match(
        self,
        query_embedding: np.ndarray,
        threshold: Optional[float] = None,
    ) -> Tuple[Optional[str], float]:
        """
        Match query embedding against registered gallery using cosine similarity.
        Returns: (best_match_id or None, best_score)
        """
        thresh = threshold if threshold is not None else self.match_threshold
        if not self._gallery:
            return None, 0.0

        best_id: Optional[str] = None
        best_sim = -1.0

        for sub_id, ref_emb in self._gallery.items():
            sim = self.compute_similarity(query_embedding, ref_emb)
            if sim > best_sim:
                best_sim = sim
                best_id = sub_id

        if best_sim >= thresh:
            return best_id, best_sim
        return None, best_sim
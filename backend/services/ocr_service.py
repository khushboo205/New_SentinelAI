from typing import Any, Dict, List
from services.model_manager import ModelManager


class OCRService:

    def __init__(self):
        manager = ModelManager()
        self.reader = manager.load_ocr()

    def read_detailed(self, image) -> List[Dict[str, Any]]:
        """Extract text tokens alongside detection confidence."""
        if self.reader is None or image is None or getattr(image, "size", 0) == 0:
            return []

        try:
            results = self.reader.readtext(image)
            return [
                {
                    "bbox": res[0],
                    "text": str(res[1]),
                    "confidence": float(res[2]),
                }
                for res in results
            ]
        except Exception:
            return []

    def read(self, image) -> List[str]:
        """Extract plain text strings from image ROI."""
        details = self.read_detailed(image)
        return [item["text"] for item in details]
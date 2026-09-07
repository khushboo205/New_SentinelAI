from core.agent import BaseAgent
from core.packet import TrackingPacket
from services.ocr_service import OCRService


class OCRAgent(BaseAgent):

    def __init__(self):

        super().__init__("OCR")

        self.ocr = OCRService()

    def process(self, packet: TrackingPacket):

        frame = packet.frame_packet.frame

        for track in packet.tracks:

            x1, y1, x2, y2 = map(int, track.detection.bbox)

            roi = frame[y1:y2, x1:x2]

            if roi.size == 0:
                continue

            details = self.ocr.read_detailed(roi)
            if details:
                track.detection.ocr_text = [d["text"] for d in details]
                track.detection.ocr_confidence = max((d["confidence"] for d in details), default=0.0)
            else:
                track.detection.ocr_text = []
                track.detection.ocr_confidence = 0.0

        return packet
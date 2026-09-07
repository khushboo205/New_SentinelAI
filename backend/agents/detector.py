from core.agent import BaseAgent
from core.packet import FramePacket, DetectionPacket
from core.models import Detection
from services.model_manager import ModelManager


class DetectorAgent(BaseAgent):

    def __init__(self, model_path: str):
        super().__init__("YOLODetector")
        self.model = ModelManager().load_yolo(model_path)

    def process(self, packet: FramePacket):

        results = self.model.predict(
            source=packet.frame,
            conf=0.35,
            verbose=False
        )
        detections = []

        names = self.model.names

        for result in results:
            for box in result.boxes:

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                class_id = int(box.cls)

                detections.append(
                    Detection(
                        bbox=(x1, y1, x2, y2),
                        confidence=float(box.conf),
                        class_id=class_id,
                        class_name=names[class_id]
                    )
                )

        return DetectionPacket(
            frame_packet=packet,
            detections=detections
        )
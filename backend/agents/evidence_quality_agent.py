import cv2
import numpy as np

from core.agent import BaseAgent
from core.packet import TrackingPacket


class EvidenceQualityAgent(BaseAgent):

    def __init__(self):
        super().__init__("EvidenceQualityAgent")

    def calculate_blur(self, image):

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        return cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()

    def calculate_brightness(self, image):

        hsv = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2HSV
        )

        return hsv[..., 2].mean()

    def process(self, packet: TrackingPacket):

        frame = packet.frame_packet.frame

        for track in packet.tracks:

            detection = track.detection

            x1, y1, x2, y2 = map(
                int,
                detection.bbox
            )

            crop = frame[y1:y2, x1:x2]

            if crop.size == 0:

                continue

            blur = self.calculate_blur(crop)

            brightness = self.calculate_brightness(crop)

            blur_score = min(blur / 200, 1.0)

            brightness_score = min(
                brightness / 255,
                1.0
            )

            overall = (
                blur_score * 0.6 +
                brightness_score * 0.4
            ) * 100

            detection.quality = {

                "blur": round(blur, 2),

                "brightness": round(
                    brightness,
                    2
                ),

                "score": round(
                    overall,
                    2
                )

            }

        return packet
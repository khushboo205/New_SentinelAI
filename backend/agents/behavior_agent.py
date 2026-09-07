from math import sqrt

from core.agent import BaseAgent
from core.packet import TrackingPacket


class BehaviorAgent(BaseAgent):

    def __init__(self):
        super().__init__("BehaviorAgent")

        # Stores history for each tracked object
        self.track_history = {}

        # Speed threshold (pixels/frame)
        self.RUNNING_THRESHOLD = 25

        # Frames required before considering loitering
        self.LOITERING_FRAMES = 200

    def process(self, packet: TrackingPacket):

        for track in packet.tracks:

            detection = track.detection
            track_id = detection.track_id

            x1, y1, x2, y2 = detection.bbox

            # Object center
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            # First appearance
            if track_id not in self.track_history:

                self.track_history[track_id] = {

                    "last_position": (cx, cy),

                    "frames": 1,

                    "speed": 0,

                    "direction": "unknown"

                }

                detection.behavior = {

                    "speed": 0,

                    "direction": "unknown",

                    "zone": "unknown",

                    "dwell_time": 0,

                    "running": False,

                    "loitering": False,

                    "restricted": False

                }

                continue

            history = self.track_history[track_id]

            last_x, last_y = history["last_position"]

            dx = cx - last_x
            dy = cy - last_y

            speed = sqrt(dx ** 2 + dy ** 2)

            # Determine movement direction
            if abs(dx) > abs(dy):

                direction = "right" if dx > 0 else "left"

            else:

                direction = "down" if dy > 0 else "up"

            history["last_position"] = (cx, cy)
            history["frames"] += 1
            history["speed"] = speed
            history["direction"] = direction

            running = speed > self.RUNNING_THRESHOLD

            loitering = (
                history["frames"] >= self.LOITERING_FRAMES
                and speed < 2
            )

            # Virtual fence / restricted zone logic:
            # Centroids located in upper buffer (cy < 350) or far boundary are flagged as restricted perimeter
            restricted = cy < 350
            zone_label = "Restricted Outer Perimeter" if restricted else "General Transit Zone"

            detection.behavior = {
                "speed": round(speed, 2),
                "direction": direction,
                "zone": zone_label,
                "dwell_time": history["frames"],
                "running": running,
                "loitering": loitering,
                "restricted": restricted,
            }

            detection.zone = zone_label
            detection.is_loitering = loitering
            detection.speed_kmh = round(speed * 1.8, 1)

        return packet
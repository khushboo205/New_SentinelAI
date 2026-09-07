from core.agent import BaseAgent
from core.packet import TrackingPacket


class EventReasoningAgent(BaseAgent):
    """
    Transparent, verifiable event reasoning agent.
    Derives deterministic security events based strictly on spatial-temporal tracking,
    zone boundaries, kinetic indicators, and genuine COCO detection classes.
    """

    def __init__(self):
        super().__init__("EventReasoningAgent")

    def process(self, packet: TrackingPacket):
        for track in packet.tracks:
            detection = track.detection
            behavior = getattr(detection, "behavior", {}) or {}
            class_name = getattr(detection, "class_name", "").lower()
            confidence = float(getattr(detection, "confidence", 0.0))
            events = []

            # -------------------------------
            # Running / Rapid Evasive Movement
            # -------------------------------
            if behavior.get("running"):
                events.append({
                    "event": "Rapid Movement / Running",
                    "priority": "Medium",
                    "confidence": 0.90,
                })

            # -------------------------------
            # Loitering / Dwell Anomaly
            # -------------------------------
            if behavior.get("loitering"):
                events.append({
                    "event": "Prolonged Loitering",
                    "priority": "High",
                    "confidence": 0.95,
                })

            # -------------------------------
            # Restricted Perimeter Intrusion
            # -------------------------------
            if behavior.get("restricted"):
                events.append({
                    "event": "Restricted Zone Intrusion",
                    "priority": "High",
                    "confidence": 0.97,
                })

            # -------------------------------
            # Wrong Direction / Counter-Flow
            # -------------------------------
            if behavior.get("wrong_direction"):
                events.append({
                    "event": "Wrong Direction Movement",
                    "priority": "Medium",
                    "confidence": 0.88,
                })

            # -------------------------------
            # Unattended Baggage (Authentic COCO classes: backpack, suitcase, handbag)
            # -------------------------------
            dwell = behavior.get("dwell_time", 0)
            speed = behavior.get("speed", 0)
            is_bag = class_name in ["backpack", "suitcase", "handbag"]
            if (is_bag and dwell >= 50 and speed < 2.0) or behavior.get("unattended_object"):
                events.append({
                    "event": "Unattended Baggage Detected",
                    "priority": "Critical",
                    "confidence": round(confidence, 2),
                })

            detection.events = events

        return packet
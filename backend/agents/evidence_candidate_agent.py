from core.agent import BaseAgent
from core.packet import TrackingPacket


class EvidenceCandidateAgent(BaseAgent):

    def __init__(self):
        super().__init__("EvidenceCandidateAgent")

    def process(self, packet: TrackingPacket):

        for track in packet.tracks:

            detection = track.detection

            evidence = []

            events = getattr(detection, "events", [])

            behavior = getattr(detection, "behavior", {})

            # ---------------------------------------
            # Event-based evidence
            # ---------------------------------------

            for event in events:

                evidence.append({

                    "type": event["event"],

                    "priority": event["priority"],

                    "confidence": event["confidence"],

                    "frame": packet.frame_packet.frame_number,

                    "track_id": detection.track_id,

                    "quality": 0,

                    "enhanced": False

                })

            # ---------------------------------------
            # Running Snapshot
            # ---------------------------------------

            if behavior.get("running"):

                evidence.append({

                    "type": "Running",

                    "priority": "Medium",

                    "confidence": 0.9,

                    "frame": packet.frame_packet.frame_number,

                    "track_id": detection.track_id,

                    "quality": 0,

                    "enhanced": False

                })

            # ---------------------------------------
            # Loitering Snapshot
            # ---------------------------------------

            if behavior.get("loitering"):

                evidence.append({

                    "type": "Loitering",

                    "priority": "High",

                    "confidence": 0.95,

                    "frame": packet.frame_packet.frame_number,

                    "track_id": detection.track_id,

                    "quality": 0,

                    "enhanced": False

                })

            detection.evidence = evidence

        return packet
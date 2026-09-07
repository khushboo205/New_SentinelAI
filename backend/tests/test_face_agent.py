def run():
    from agents.input_manager import InputManagerAgent
    from agents.detector import DetectorAgent
    from agents.tracker import TrackingAgent
    from agents.face import FaceAgent
    from config.config import YOLO_MODEL
    from pathlib import Path

    VIDEO = "data/videos/input/test.mp4"
    if not Path(VIDEO).exists():
        return

    input_agent = InputManagerAgent(VIDEO)
    detector = DetectorAgent(str(YOLO_MODEL))
    tracker = TrackingAgent(str(YOLO_MODEL))
    face = FaceAgent()

    input_agent.initialize()
    detector.initialize()
    tracker.initialize()
    face.initialize()

    packet = input_agent.process()
    if packet is not None:
        packet = detector.process(packet)
        packet = tracker.process(packet)
        packet = face.process(packet)

        for track in packet.tracks:
            print(track.track_id)
            print(track.detection.class_name)
            print(track.detection.face_detected)
            if track.detection.face_embedding is not None:
                print(len(track.detection.face_embedding))

    face.shutdown()
    tracker.shutdown()
    detector.shutdown()
    input_agent.shutdown()


if __name__ == "__main__":
    run()
def run():
    from agents.input_manager import InputManagerAgent
    from agents.detector import DetectorAgent
    from agents.tracker import TrackingAgent
    from agents.face import FaceAgent
    from agents.reid import ReIDAgent
    from config.config import YOLO_MODEL
    from pathlib import Path

    VIDEO = "data/videos/input/test.mp4"
    if not Path(VIDEO).exists():
        return

    input_agent = InputManagerAgent(VIDEO)
    detector = DetectorAgent(str(YOLO_MODEL))
    tracker = TrackingAgent(str(YOLO_MODEL))
    face = FaceAgent()
    reid = ReIDAgent()

    input_agent.initialize()
    detector.initialize()
    tracker.initialize()
    face.initialize()
    reid.initialize()

    packet = input_agent.process()
    if packet is not None:
        packet = detector.process(packet)
        packet = tracker.process(packet)
        packet = face.process(packet)
        packet = reid.process(packet)

        for track in packet.tracks:
            print(track.track_id)
            print(track.detection.class_name)
            print(track.detection.reid_embedding is not None)

    reid.shutdown()
    face.shutdown()
    tracker.shutdown()
    detector.shutdown()
    input_agent.shutdown()


if __name__ == "__main__":
    run()
def run():
    from agents.input_manager import InputManagerAgent
    from agents.detector import DetectorAgent
    from agents.tracker import TrackingAgent
    from agents.feature_extractor import FeatureExtractorAgent
    from config.config import YOLO_MODEL
    from pathlib import Path

    VIDEO = "data/videos/sample2.mp4"
    if not Path(VIDEO).exists():
        return

    input_agent = InputManagerAgent(VIDEO)
    detector = DetectorAgent(str(YOLO_MODEL))
    tracker = TrackingAgent(str(YOLO_MODEL))
    feature = FeatureExtractorAgent()

    input_agent.initialize()
    detector.initialize()
    tracker.initialize()
    feature.initialize()

    packet = input_agent.process()
    if packet is not None:
        packet = detector.process(packet)
        packet = tracker.process(packet)
        packet = feature.process(packet)

        for track in packet.tracks:
            print(track.track_id)
            print(track.detection.attributes)

    feature.shutdown()
    tracker.shutdown()
    detector.shutdown()
    input_agent.shutdown()


if __name__ == "__main__":
    run()
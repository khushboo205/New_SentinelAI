def run():
    from agents.input_manager import InputManagerAgent
    from agents.detector import DetectorAgent
    from agents.tracker import TrackingAgent
    from agents.quality_assessor import QualityAssessmentAgent
    from pathlib import Path

    VIDEO = "data/videos/sample2.mp4"
    if not Path(VIDEO).exists():
        return

    MODEL = "yolo11n.pt"

    input_agent = InputManagerAgent(VIDEO)
    detector = DetectorAgent(MODEL)
    tracker = TrackingAgent(MODEL)
    quality = QualityAssessmentAgent()

    input_agent.initialize()
    detector.initialize()
    tracker.initialize()
    quality.initialize()

    packet = input_agent.process()
    if packet is not None:
        detection_packet = detector.process(packet)
        tracking_packet = tracker.process(detection_packet)
        quality_packet = quality.process(tracking_packet)

        for track in quality_packet.tracks:
            print(
                track.track_id,
                track.detection.class_name,
                round(track.detection.quality_score, 2),
                track.detection.is_blurry,
            )

    quality.shutdown()
    tracker.shutdown()
    detector.shutdown()
    input_agent.shutdown()


if __name__ == "__main__":
    run()
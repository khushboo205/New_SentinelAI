def run():
    from agents.input_manager import InputManagerAgent
    from agents.detector import DetectorAgent
    from agents.tracker import TrackingAgent
    from agents.event_detector import EventDetectorAgent
    from pathlib import Path

    VIDEO = "data/videos/sample2.mp4"
    if not Path(VIDEO).exists():
        return

    MODEL = "yolo11n.pt"

    input_agent = InputManagerAgent(VIDEO)
    detector = DetectorAgent(MODEL)
    tracker = TrackingAgent(MODEL)
    event = EventDetectorAgent()

    input_agent.initialize()
    detector.initialize()
    tracker.initialize()
    event.initialize()

    packet = input_agent.process()
    if packet is not None:
        packet = detector.process(packet)
        packet = tracker.process(packet)
        packet = event.process(packet)

    event.shutdown()
    tracker.shutdown()
    detector.shutdown()
    input_agent.shutdown()


if __name__ == "__main__":
    run()
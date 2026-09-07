def run():
    from agents.input_manager import InputManagerAgent
    from agents.detector import DetectorAgent
    from agents.tracker import TrackingAgent
    from agents.ocr import OCRAgent
    from pathlib import Path

    VIDEO = "data/videos/sample2.mp4"
    if not Path(VIDEO).exists():
        return

    MODEL = "yolo11n.pt"

    input_agent = InputManagerAgent(VIDEO)
    detector = DetectorAgent(MODEL)
    tracker = TrackingAgent(MODEL)
    ocr = OCRAgent()

    input_agent.initialize()
    detector.initialize()
    tracker.initialize()
    ocr.initialize()

    packet = input_agent.process()
    if packet is not None:
        packet = detector.process(packet)
        packet = tracker.process(packet)
        packet = ocr.process(packet)

        for track in packet.tracks:
            print(track.track_id)
            print(track.detection.class_name)
            print(track.detection.ocr_text)
            print("-" * 40)

    ocr.shutdown()
    tracker.shutdown()
    detector.shutdown()
    input_agent.shutdown()


if __name__ == "__main__":
    run()
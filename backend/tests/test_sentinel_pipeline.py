def run():
    import cv2
    from agents.input_manager import InputManagerAgent
    from agents.detector import DetectorAgent
    from agents.tracker import TrackingAgent
    from services.visualizer import Visualizer

    VIDEO = "data/videos/sample2.mp4"
    MODEL = "yolo11n.pt"

    input_agent = InputManagerAgent(VIDEO)
    detector = DetectorAgent(MODEL)
    tracker = TrackingAgent(MODEL)
    visualizer = Visualizer()

    input_agent.initialize()
    detector.initialize()
    tracker.initialize()

    while True:
        frame_packet = input_agent.process()
        if frame_packet is None:
            break

        detection_packet = detector.process(frame_packet)
        tracking_packet = tracker.process(detection_packet)
        image = visualizer.draw(tracking_packet)
        image = cv2.resize(image, (960, 540))
        cv2.imshow("SentinelAI", image)

        if cv2.waitKey(30) & 0xFF == ord("q"):
            break

    input_agent.shutdown()
    detector.shutdown()
    tracker.shutdown()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run()
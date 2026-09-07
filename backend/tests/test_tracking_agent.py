def run():
    from agents.input_manager import InputManagerAgent
    from agents.tracker import TrackingAgent
    from core.packet import DetectionPacket
    from pathlib import Path

    VIDEO = "data/videos/sample2.mp4"
    if not Path(VIDEO).exists():
        return

    input_agent = InputManagerAgent(VIDEO)
    tracker = TrackingAgent("yolo11n.pt")

    input_agent.initialize()
    tracker.initialize()

    packet = input_agent.process()
    count = 0
    while packet is not None and count < 10:
        count += 1
        detection_packet = DetectionPacket(frame_packet=packet)
        tracking_packet = tracker.process(detection_packet)
        for track in tracking_packet.tracks:
            print(track.track_id, track.detection.class_name)
        packet = input_agent.process()

    tracker.shutdown()
    input_agent.shutdown()


if __name__ == "__main__":
    run()
if __name__ == "__main__":
    from agents.input_manager import InputManagerAgent
    from pathlib import Path

    video_path = "data/videos/input/sample.mp4"
    if Path(video_path).exists():
        agent = InputManagerAgent(video_path)
        agent.initialize()
        for _ in range(5):
            packet = agent.process()
            if packet is None:
                break
            print(packet.frame_id, packet.frame.shape)
        agent.shutdown()
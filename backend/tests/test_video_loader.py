if __name__ == "__main__":
    from services.video_loader import VideoLoader
    from pathlib import Path

    video_path = "data/videos/input/sample.mp4"
    if Path(video_path).exists():
        loader = VideoLoader(video_path)
        print(loader.width, loader.height, loader.fps, loader.frame_count)
        success, frame = loader.read()
        print(success, frame.shape if frame is not None else None)
        loader.release()
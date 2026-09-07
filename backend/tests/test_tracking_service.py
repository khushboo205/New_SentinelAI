def run():
    from services.tracker import TrackingService
    import cv2
    from pathlib import Path

    video_path = "data/videos/sample2.mp4"
    if not Path(video_path).exists():
        print("Sample video not found.")
        return

    tracker = TrackingService("yolo11n.pt")
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    if success and frame is not None:
        results = tracker.track(frame)
        print(results[0].boxes)
        print(results[0].boxes.id)
    cap.release()


if __name__ == "__main__":
    run()
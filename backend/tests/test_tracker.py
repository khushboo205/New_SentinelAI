def run():
    import cv2
    from ultralytics import YOLO

    model = YOLO("yolo11n.pt")
    cap = cv2.VideoCapture("data/videos/sample2.mp4")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        results = model.track(
            source=frame,
            persist=True,
            conf=0.35,
            verbose=False,
        )

        annotated = results[0].plot()
        if results[0].boxes.id is not None:
            print("Track IDs:", results[0].boxes.id.cpu().numpy())

        cv2.imshow("ByteTrack Test", annotated)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run()
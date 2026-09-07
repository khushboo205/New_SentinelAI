def run():
    from ultralytics import YOLO
    import cv2

    MODEL_PATH = "yolo11n.pt"
    VIDEO_PATH = "data/videos/sample2.mp4"

    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(VIDEO_PATH)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame, conf=0.20, verbose=False)
        annotated = results[0].plot()
        display = cv2.resize(annotated, (960, 540))
        cv2.imshow("YOLO11 Video Test", display)

        key = cv2.waitKey(40) & 0xFF
        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run()
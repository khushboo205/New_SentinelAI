def run():
    from ultralytics import YOLO
    import cv2

    MODEL_PATH = "yolo11n.pt"

    try:
        print("Loading model...")
        model = YOLO(MODEL_PATH)
        print("✅ Model loaded successfully!")

        image = cv2.imread("data/images/market.jpg")
        if image is None:
            print("❌ Test image not found.")
            return

        print("Running inference...")
        results = model.predict(image, conf=0.20, verbose=False)
        print("✅ Inference completed!")

        result = results[0]
        print(f"\nTotal Detections : {len(result.boxes)}")

        for i, box in enumerate(result.boxes):
            cls = int(box.cls)
            conf = float(box.conf)
            print(f"{i+1}. {model.names[cls]} | Confidence = {conf:.3f}")
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                image,
                f"{model.names[cls]} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

        cv2.imshow("YOLO Test", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    except Exception as e:
        print(type(e).__name__)
        print(e)


if __name__ == "__main__":
    run()
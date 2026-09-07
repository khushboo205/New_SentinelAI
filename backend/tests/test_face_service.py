def run():
    import cv2
    from services.face_service import FaceService
    from pathlib import Path

    img_path = "data/images/market.jpg"
    if not Path(img_path).exists():
        return

    image = cv2.imread(img_path)
    service = FaceService()
    faces = service.detect(image)
    print("Faces found:", len(faces))
    for face in faces:
        print(getattr(face, "bbox", None))


if __name__ == "__main__":
    run()
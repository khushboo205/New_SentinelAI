if __name__ == "__main__":
    import cv2
    from services.quality_assessor import QualityAssessor
    from pathlib import Path

    img_path = "data/images/market.jpg"
    if Path(img_path).exists():
        image = cv2.imread(img_path)
        qa = QualityAssessor()
        blurry, score = qa.is_blurry(image)
        print("Blur Score :", score)
        print("Blurry     :", blurry)
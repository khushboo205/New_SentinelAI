from services.model_manager import ModelManager


class FaceService:

    def __init__(self):

        manager = ModelManager()

        self.app = manager.load_face()

    def detect(self, image):
        if self.app is None or image is None or getattr(image, "size", 0) == 0:
            return []

        try:
            faces = self.app.get(image)
            return faces or []
        except Exception:
            return []
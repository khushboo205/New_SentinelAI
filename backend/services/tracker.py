from services.model_manager import ModelManager

class TrackingService:

    def __init__(self, model_path: str):

        manager = ModelManager()

        self.model = manager.load_yolo(model_path)

    def track(self, frame):

        return self.model.track(
            source=frame,
            tracker="bytetrack.yaml",
            persist=True,
            conf=0.35,
            verbose=False,
        )
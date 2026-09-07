from core.pipeline_manager import PipelineManager

class PipelineManagerService:

    _instance = None

    @classmethod
    def get_pipeline(cls):

        if cls._instance is None:
            cls._instance = PipelineManager()

        return cls._instance
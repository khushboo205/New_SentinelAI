from config.config import YOLO_MODEL

from agents.behavior_agent import BehaviorAgent
from agents.event_reasoning_agent import EventReasoningAgent
from agents.input_manager import InputManagerAgent
from agents.enhancement import EnhancementAgent
from agents.detector import DetectorAgent
from agents.tracker import TrackingAgent
from agents.feature_extractor import FeatureExtractorAgent
from agents.face import FaceAgent
from agents.ocr import OCRAgent
from agents.reid import ReIDAgent
from agents.event_agent import EventAgent
from agents.suspicion_agent import SuspicionAgent
from agents.database_agent import DatabaseAgent

from core.pipeline_manager import PipelineManager


def create_pipeline(video_path):

    agents = [

        InputManagerAgent(video_path),

        EnhancementAgent(),

        DetectorAgent(str(YOLO_MODEL)),

        TrackingAgent(str(YOLO_MODEL)),

        BehaviorAgent(),

        EventReasoningAgent(),

        FeatureExtractorAgent(),

        FaceAgent(),

        OCRAgent(),

        ReIDAgent(),

        EventAgent(),

        SuspicionAgent(),

        DatabaseAgent()

    ]

    pipeline = PipelineManager(agents)

    return pipeline, agents
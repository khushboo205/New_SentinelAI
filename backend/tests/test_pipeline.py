if __name__ == "__main__":
    from core.agent import BaseAgent
    from core.packet import FramePacket
    from core.pipeline import Pipeline

    class AddOneAgent(BaseAgent):
        def __init__(self):
            super().__init__("AddOne")

        def process(self, packet):
            packet.frame_id += 1
            return packet

    class DoubleAgent(BaseAgent):
        def __init__(self):
            super().__init__("Double")

        def process(self, packet):
            packet.frame_id *= 2
            return packet

    pipeline = Pipeline()
    pipeline.add_agent(AddOneAgent())
    pipeline.add_agent(DoubleAgent())
    pipeline.initialize()

    packet = FramePacket(frame_id=5)
    result = pipeline.run(packet)
    print("Pipeline result frame_id:", result.frame_id)
    pipeline.shutdown()
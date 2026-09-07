if __name__ == "__main__":
    from core.agent import BaseAgent
    from core.packet import FramePacket

    class DummyAgent(BaseAgent):
        def __init__(self):
            super().__init__("DummyAgent")

        def process(self, packet):
            self.logger.info("Processing packet.")
            return packet

    agent = DummyAgent()
    agent.initialize()
    packet = FramePacket(frame_id=1)
    result = agent.process(packet)
    print(result)
    agent.shutdown()
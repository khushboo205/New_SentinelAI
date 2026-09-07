from typing import Any, Generator, List, Optional


class PipelineManager:

    def __init__(self, agents: List[Any]):
        self.agents = agents

    def initialize(self) -> None:
        """Initialize all pipeline agents sequentially."""
        for agent in self.agents:
            agent.initialize()

    def run_frame(self) -> Optional[Any]:
        """Process a single frame through all agents."""
        packet = self.agents[0].process()
        if packet is None:
            return None

        for agent in self.agents[1:]:
            packet = agent.process(packet)
            if packet is None:
                break

        return packet

    def stream(self, max_frames: Optional[int] = None) -> Generator[Any, None, None]:
        """Generator that streams processed packets until max_frames or EOF."""
        count = 0
        while max_frames is None or count < max_frames:
            packet = self.run_frame()
            if packet is None:
                break
            count += 1
            yield packet

    def run_all(self, max_frames: Optional[int] = None) -> List[Any]:
        """Execute pipeline across multiple frames and return all generated packets."""
        packets = []
        for packet in self.stream(max_frames=max_frames):
            packets.append(packet)
        return packets

    def run(self, max_frames: int = 1) -> Optional[Any]:
        """
        Run pipeline for 1 frame (backward compatible with original API)
        or up to max_frames, returning the final packet.
        """
        last_packet = None
        for packet in self.stream(max_frames=max_frames):
            last_packet = packet
        return last_packet

    def shutdown(self) -> None:
        """Shutdown all agents in reverse order."""
        for agent in reversed(self.agents):
            agent.shutdown()
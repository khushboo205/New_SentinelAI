if __name__ == "__main__":
    from core.message_bus import MessageBus
    from core.packet import FramePacket

    bus = MessageBus()

    def receiver(packet):
        print(f"Received Frame ID: {packet.frame_id}")

    bus.subscribe("frame", receiver)
    packet = FramePacket(frame_id=10)
    bus.publish("frame", packet)
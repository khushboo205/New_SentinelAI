from core.pipeline_factory import create_pipeline

VIDEO = "data/videos/input/test.mp4"

pipeline, agents = create_pipeline(VIDEO)

pipeline.initialize()

packet = pipeline.run()

for track in packet.tracks:

    print(track.detection.behavior)

# print results

for agent in reversed(agents):
    agent.shutdown()
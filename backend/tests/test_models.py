if __name__ == "__main__":
    from core.models import Detection, Track

    person = Detection(
        class_id=0,
        class_name="person",
        confidence=0.95,
        bbox=(100.0, 150.0, 250.0, 500.0),
    )
    track = Track(
        track_id=1,
        detection=person,
    )
    print(person)
    print(track)
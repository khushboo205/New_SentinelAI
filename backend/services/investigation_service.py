from database.repository import Repository


class InvestigationService:

    def __init__(self):

        self.repository = Repository()

    def get_investigation(self, track_id):

        return {

            "track": self.repository.get_track(track_id),

            "events": self.repository.get_events(track_id),

            "features": self.repository.get_features(track_id),

            "faces": self.repository.get_face(track_id),

            "ocr": self.repository.get_ocr(track_id),

            "risk": self.repository.get_risk(track_id),

            "timeline": self.repository.get_timeline(track_id)

        }

    def get_tracks(self):

        return self.repository.get_tracks()

    def save_summary(
        self,
        track
    ):

        summary = (
            f"{track.detection.class_name} "
            f"(Track {track.track_id}) "
            f"Risk={track.detection.risk_score}"
        )

        self.repository.save_investigation(

            track.track_id,

            track.detection.class_name,

            track.detection.risk_score,

            summary

        )

    def save_timeline(
        self,
        track
    ):

        for event in track.detection.events:

            self.repository.save_timeline(

                track.track_id,

                event

            )

    def update(
        self,
        packet
    ):

        for track in packet.tracks:

            self.save_summary(track)

            self.save_timeline(track)
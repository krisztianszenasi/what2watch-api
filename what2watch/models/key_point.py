from what2watch.extensions import db


class KeyPoint(db.Model):

    _id = db.Column('id', db.Integer, primary_key=True)
    video_id = db.Column(db.String(14), db.ForeignKey('video.id'))
    text = db.Column(db.Text)
    video = db.relationship('Video', back_populates='key_points')
    starts_from_id = db.Column(db.Integer, db.ForeignKey('transcript_chunk.id'), nullable=True)
    starts_from = db.relationship('TranscriptChunk')
    starting_words = db.Column(db.Text)

    def as_dict(self) -> dict:
        return {
            'id:': self._id,
            'text': self.text,
            'url': self.starts_from.url if self.starts_from else None,
        }
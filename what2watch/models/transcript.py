from what2watch.extensions import db
from what2watch.models import video


class TranscriptChunk(db.Model):

    _id = db.Column('id', db.Integer, primary_key=True)
    video_id = db.Column(db.String(14), db.ForeignKey('video.id'))
    text = db.Column(db.Text)
    start = db.Column(db.Float)
    duration = db.Column(db.Float)
    video = db.relationship('Video', back_populates='transcript_chunks')

    def as_dict(self) -> dict:
        return {
            'id': self._id,
            'video_id': self.video_id,
            'text': self.text,
            'start': self.start,
            'duration': self.duration,
            'timestamp': self.timestamp,
            'url': self.url,
        }
    
    @property
    def timestamp(self) -> str:
        minutes, seconds = divmod(self.start, 60)
        hours, minutes = divmod(minutes, 60)

        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)

        if hours > 0:
            return f'{hours}h{minutes}m{seconds}s'
        elif minutes > 0:
            return f'{minutes}m{seconds}s'
        else:
            return f'{seconds}s'

    @property
    def url(self) -> str:
        return f'{self.video.url}&t={self.timestamp}'
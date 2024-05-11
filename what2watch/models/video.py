from what2watch.extensions import db


class Video(db.Model):

    _id = db.Column('id', db.String(14), primary_key=True)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    view_count = db.Column(db.Integer)
    thumbnail_url = db.Column(db.Text)
    publish_date = db.Column(db.DateTime)
    length = db.Column(db.Integer)
    author = db.Column(db.Text)
    summary = db.Column(db.Text)
    key_points = db.relationship('KeyPoint', back_populates='video')
    transcript_chunks = db.relationship('TranscriptChunk', back_populates='video')
    
    def as_dict(self) -> dict:
        return {
            'id': self._id,
            'title': self.title,
            'description': self.description,
            'view_count': self.view_count,
            'thumbnail_url': self.thumbnail_url,
            'publish_date': self.publish_date,
            'length': self.length,
            'author': self.author,
            'url': self.url
        }
    
    @property
    def url(self) -> str:
        return f'https://www.youtube.com/watch?v={self._id}'
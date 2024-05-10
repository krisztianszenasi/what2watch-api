from what2watch.extensions import db


class KeyPoint(db.Model):

    _id = db.Column('id', db.Integer, primary_key=True)
    video_id = db.Column(db.String(14), db.ForeignKey('video.id'))
    text = db.Column(db.Text)
    timestamp = db.Column(db.Float)
    video = db.relationship('Video', back_populates='key_points')
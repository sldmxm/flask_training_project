from datetime import datetime

from settings import Config
from . import db


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(
        db.String(Config.MAX_URL_LENGTH),
        nullable=False
    )
    short = db.Column(
        db.String(Config.MAX_CUSTOM_ID_LENGTH),
        unique=True,
        nullable=False
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

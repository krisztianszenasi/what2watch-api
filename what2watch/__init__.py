from flask import Flask

from what2watch.extensions import db, migrate
from what2watch.models import Video, KeyPoint
from dotenv import load_dotenv
from what2watch.config import Config
from what2watch.routes.transcript import transcript


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    return app

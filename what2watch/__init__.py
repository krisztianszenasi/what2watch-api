from flask import Flask

from what2watch.extensions import db, migrate
from dotenv import load_dotenv
from what2watch.routes.transcript import transcript


def create_app(config='what2watch.config.default'):
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(transcript)

    return app

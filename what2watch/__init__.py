from flask import Flask

from what2watch.extensions import db, migrate
from dotenv import load_dotenv
from what2watch.routes.video import video
import os


def create_app(config='what2watch.config.default'):
    load_dotenv()

    if os.environ.get('OPENAI_API_KEY') is None:
        print('\nPlease set your OpenAI API key as an environmental variable: OPENAI_API_KEY')
        print('\nGet one here: https://platform.openai.com/')
        exit()

    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(video)

    return app

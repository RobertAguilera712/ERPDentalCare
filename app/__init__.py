from flask import Flask 

from .extensions import api, db
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    api.init_app(app)
    db.init_app(app)

    return app
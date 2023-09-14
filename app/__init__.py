from flask import Flask 

from .extensions import api, db
from .config import Config
from .patients.controller import patients_ns
from .get.controller import get_ns


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    api.init_app(app)
    db.init_app(app)
    api.add_namespace(patients_ns)
    api.add_namespace(get_ns)


    return app
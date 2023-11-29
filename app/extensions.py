from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Namespace, abort
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import current_user
from onesignal_sdk.client import Client

api = Api()
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()

onesignal_app_id = "93573d5a-e00c-4bfd-8ead-439a5b74e6eb"
onesignal_rest_api_key = "Nzk5MDUyNmMtYzQwYS00MDY3LThkMjQtY2U2ZTk2MDY0MjJj"

onesignal_client = Client(app_id=onesignal_app_id, rest_api_key=onesignal_rest_api_key)

from app.models import RowStatus

parser = api.parser()
parser.add_argument(
    "status",
    type=str,
    help="The status of the registers returned from this endpoint",
    required=False,
)

authorizations = {
    "jsonWebToken": {"type": "apiKey", "in": "header", "name": "Authorization"}
}


def role_required(allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if current_user is None:
                abort(404, "The user does not exists")

            if current_user.role not in allowed_roles:
                abort(
                    403,
                    f"{current_user.email} You do not have the permissions to access to this route",
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator

from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Namespace, abort
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import current_user

api = Api()
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()

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
                abort(403, f"{current_user.email} You do not have the permissions to access to this route")

            return fn(*args, **kwargs)

        return wrapper

    return decorator

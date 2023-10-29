from flask_restx import fields
from app.extensions import api

login_request = api.model(
    "login_request",
    {
        "email": fields.String(description="The email of the user", required=True),
        "password": fields.String(
            description="The password of the user", required=True
        ),
    },
)

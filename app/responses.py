from flask_restx import fields
from .extensions import api
from .get.responses import tax_regime_response




person_response = api.model(
    "person_response",
    {
        "id": fields.Integer(description="Unique identifier for the person"),
        "name": fields.String(description="Name of the person"),
        "surname": fields.String(description="Surname of the person"),
        "lastname": fields.String(description="Lastname of the person"),
        "birthday": fields.Date(description="Birthday of the person"),
        "rfc": fields.String(description="RFC of the person"),
        "tax_regime": fields.Nested(tax_regime_response),
        "sex": fields.Boolean(description="Sex of the person"),
        "address": fields.String(description="Address of the person"),
        "cp": fields.String(description="Postal code"),
        "latitude": fields.Float(description="Latitude of the person"),
        "longitude": fields.Float(description="Longitude of the person"),
        "phone": fields.String(description="Phone number of the person"),
    },
)

user_response = api.model(
    "user_response",
    {
        "id": fields.Integer(description="Unique identifier for the user"),
        "email": fields.String(description="Email address of the user"),
        "image": fields.String(description="User image as base64 text"),
    },
)

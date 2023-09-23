from flask_restx import fields
from .extensions import api

person_request = api.model(
    "person_request",
    {
        "name": fields.String(
            required=True, description="Name of the person", max_length=45
        ),
        "surname": fields.String(
            required=True, description="Surname of the person", max_length=45
        ),
        "lastname": fields.String(
            required=True, description="Lastname of the person", max_length=45
        ),
        "birthday": fields.Date(required=True, description="Birthday of the person"),
        "rfc": fields.String(description="RFC of the person", max_length=13),
        "tax_regime_id": fields.Integer(
            required=True, description="The id of the tax regime for this person"
        ),
        "sex": fields.Boolean(required=True, description="Sex of the person"),
        "address": fields.String(
            required=True, description="Address of the person", max_length=255
        ),
        "cp": fields.String(required=True, description="Postal code", max_length=10),
        "latitude": fields.String(required=True, description="Latitude of the person", max_length=20),
        "longitude": fields.String(required=True, description="Longitude of the person", max_length=20),
        "phone": fields.String(
            required=True, description="Phone number of the person", max_length=12
        ),
    },
)


user_request = api.model(
    "user_requst",
    {
        "email": fields.String(
            required=True, description="Email address of the user", max_length=100
        ),
        "image": fields.String(description="User image as base64 text"),
        "password": fields.String(
            required=True, description="Password of the user", max_length=60
        ),
    },
)

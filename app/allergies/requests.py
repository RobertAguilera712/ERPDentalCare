from flask_restx import fields
from app.extensions import api

allergy_request = api.model(
    "allergy_request",
    {"name": fields.String(description="The name of the allergy", required=True)},
)

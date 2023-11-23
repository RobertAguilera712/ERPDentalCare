from flask_restx import fields
from app.extensions import api

allergy_response = api.model(
    "allergy_response",
    {
        "id": fields.Integer(description="The id of the allergy"),
        "name": fields.String(description="The name of the allergy"),
        "status": fields.String(
            description="The status of the allergy", attribute="status.name"
        ),
    },
)

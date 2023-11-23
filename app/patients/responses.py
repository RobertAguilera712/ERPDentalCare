from flask_restx import fields
from app.extensions import api
from app.responses import user_response, person_response
from app.get.responses import allergy_response

patient_response = api.model(
    "patient_response",
    {
        "id": fields.Integer(description="Unique identifier for the patient"),
        "person": fields.Nested(person_response),
        "user": fields.Nested(user_response),
        "allergies": fields.Nested(allergy_response),
        "status": fields.String(
            description="The status of this patient", attribute="status.name"
        ),
    },
)

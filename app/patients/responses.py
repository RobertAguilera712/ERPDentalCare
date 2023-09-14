from flask_restx import fields
from app.extensions import api
from app.responses import user_response, person_response

patient_response = api.model(
    "patient_response",
    {
        "person": fields.Nested(person_response),
        "user": fields.Nested(user_response),
    },
)
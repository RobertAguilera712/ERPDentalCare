from flask_restx import fields
from app.extensions import api
from app.requests import user_request, person_request
from app.get.responses import allergy_response


patient_request = api.model(
    "patient_request",
    {
        "person": fields.Nested(person_request),
        "user": fields.Nested(user_request),
        "allergies": fields.List(fields.Nested(allergy_response), description="The list of allergies that the patient has retrieved from api/get/allergies. If a new allergy needs to be added. Send the request with id of 0")
    },
)

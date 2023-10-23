from flask_restx import fields
from app.extensions import api

create_appointment_request = api.model(
    "create_appointment_request",
    {
        "dentist_id": fields.Integer(
            required=True,
            description="The id of the dentist to which we want to create this appointment",
        ),
        "patient_id": fields.Integer(
            required=True,
            description="The id of the patient to which we want to create this appointment",
        ),
        "schedules": fields.List(fields.Integer, description="The id's of the schedules that will be used to register this appointment", required=True),
    },
)

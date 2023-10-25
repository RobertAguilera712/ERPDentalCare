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
        "start_date": fields.DateTime(required=True, description="The datetime in which this appointment will start"),
        "end_date": fields.DateTime(required=True, description="The datetime in which this appointment will end"),
    },
)

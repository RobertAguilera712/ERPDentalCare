from flask_restx import fields
from app.extensions import api
from app.dentists.responses import dentist_response
from app.patients.responses import patient_response

appointment_response = api.model(
    "appointment_response",
    {
        "id": fields.Integer(description="The unique identifier for this appointment"),
        "dentist": fields.Nested(
            dentist_response,
            description="The dentist which this appointment was created for",
        ),
        "patient": fields.Nested(
            patient_response,
            description="The patient which this appointment was created for",
        ),
        "start_date": fields.DateTime(
            description="The date in which the schedule will start"
        ),
        "end_date": fields.DateTime(
            description="The date in which the schedule will end"
        ),
        "sells": fields.List(
            fields.String(
                description="The sells that were generated in this appointment. TODO"
            )
        ),
    },
)

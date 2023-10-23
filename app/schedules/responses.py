from flask_restx import fields
from app.extensions import api
from app.dentists.responses import dentist_response

schedule_response = api.model(
    "schedule_response",
    {
        "id": fields.Integer(
            description="The unique identifier for this schedule"
        ),
        "dentist_id": fields.Integer(
            description="The id of the dentist which this schedule was created for"
        ),
        "start_date": fields.DateTime(
            description="The date in which the schedule will start"
        ),
        "end_date": fields.DateTime(description="The date in which the schedule will end"),
        "appointment_id": fields.Integer(
            description="The id of the appoint that is assigned for this schedule"
        ),
    },
)

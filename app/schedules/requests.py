from flask_restx import fields
from app.extensions import api

create_schedule_request = api.model(
    "create_schedule_request",
    {
        "dentist_id": fields.Integer(
            required=True,
            description="The id of the dentist to which we want to create his schedule",
        ),
        "start_date": fields.Date(
            required=True, description="The date in which the schedule will start"
        ),
        "end_date": fields.Date(
            required=True, description="The date in which the schedule will end"
        ),
    },
)

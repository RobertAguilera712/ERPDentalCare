from flask_restx import fields
from app.extensions import api
from app.requests import user_request, person_request, edit_user_request
from app.get.responses import weekday_response, frequency_response


diploma_request = api.model(
    "diploma_request",
    {
        "name": fields.String(
            required=True, description="The name of the diploma", max_length=80
        ),
        "university": fields.String(
            required=True, description="The name of the diploma", max_length=80
        ),
    },
)

dentist_request = api.model(
    "dentist_request",
    {
        "person": fields.Nested(person_request),
        "user": fields.Nested(user_request),
        "professional_license": fields.String(
            required=True, description="Name of the person", max_length=45
        ),
        "hired_at": fields.Date(
            required=True, description="The date in which this dentist was hired"
        ),
        "position": fields.String(
            required=True,
            description="The position that this dentist has in the dental office",
            max_length=60,
        ),
        "diplomas": fields.List(fields.Nested(diploma_request)),
    },
)

edit_dentist_request = api.model(
    "dentist_request",
    {
        "person": fields.Nested(person_request),
        "user": fields.Nested(edit_user_request),
        "professional_license": fields.String(
            required=True, description="Name of the person", max_length=45
        ),
        "hired_at": fields.Date(
            required=True, description="The date in which this dentist was hired"
        ),
        "position": fields.String(
            required=True,
            description="The position that this dentist has in the dental office",
            max_length=60,
        ),
        "diplomas": fields.List(fields.Nested(diploma_request)),
    },
)

schedule_request = api.model("schedule_request", {
        "start_date": fields.Date(
            required=True, description="The date in from which the schedule will be created"
        ),
        "end_date": fields.Date(
            required=True, description="The date in which the schedule will end"
        ),
})

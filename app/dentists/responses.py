from flask_restx import fields
from app.extensions import api
from app.responses import user_response, person_response
from app.get.responses import weekday_response, frequency_response


diploma_response = api.model(
    "diploma_response",
    {
        "id": fields.Integer(description="Unique identifier for the diploma"),
        "name": fields.String(
            required=True, description="The name of the diploma", max_length=80
        ),
        "university": fields.String(
            required=True, description="The name of the diploma", max_length=80
        ),
    },
)

dentist_response = api.model(
    "dentist_response",
    {
        "id": fields.Integer(description="Unique identifier for the dentist"),
        "person": fields.Nested(person_response),
        "user": fields.Nested(user_response),
        "professional_license": fields.String(
            required=True, description="Name of the person"
        ),
        "hired_at": fields.Date(
            required=True, description="The date in which this dentist was hired"
        ),
        "position": fields.String(
            required=True,
            description="The position that this dentist has in the dental office",
        ),
        "weekdays": fields.List(fields.Nested(weekday_response)),
        "start_time": fields.Time(
            required=True, description="The time in which the dentist starts to work"
        ),
        "end_time": fields.Time(
            required=True, description="The time in which the dentist ends to work"
        ),
        "frequency": fields.Nested(frequency_response),
        "diplomas": fields.List(fields.Nested(diploma_response)),
    },
)

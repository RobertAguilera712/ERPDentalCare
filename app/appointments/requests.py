from flask_restx import fields
from app.extensions import api
from app.models import AppointmentStatus

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
        "start_date": fields.DateTime(
            required=True,
            description="The datetime in which this appointment will start",
        ),
        "end_date": fields.DateTime(
            required=True, description="The datetime in which this appointment will end"
        ),
    },
)

get_appointments_request = api.model(
    "get_appointments_request",
    {
        "dentist_id": fields.Integer(
            description="The id of the dentist to which we want to retrieve his appointment.",
        ),
        "patient_id": fields.Integer(
            description="The id of the patient to which we want to retrieve his appointment.",
        ),
        "status": fields.String(
            description="The status of the appointments that we want to receive",
            enum=[status.name for status in AppointmentStatus],
        ),
        "start_date": fields.DateTime(
            required=True,
            description="The start date from which when want to retrieve the appointments",
        ),
        "end_date": fields.DateTime(
            required=True,
            description="The end date from which when want to retrieve the appointments",
        ),
    },
)

service_sell_request = api.model(
    "service_sell_request",
    {
        "service_id": fields.Integer(
            required=True,
            description="The id of the service which was sold on this sell",
        ),
        "quantity": fields.Integer(
            required=True,
            description="The amount of times that this service was given to the patient",
            min=1,
        ),
    },
)

supply_sell_request = api.model(
    "supply_sell_request",
    {
        "supply_id": fields.Integer(
            required=True,
            description="The id of the supply which was sold on this sell",
        ),
        "quantity": fields.Integer(
            required=True,
            description="The amount of times that this service was given to the patient",
            min=1,
        ),
    },
)


finish_appointment_request = api.model(
    "finish_appointment_request",
    {
        "services": fields.List(
            fields.Nested(service_sell_request),
            description="The services that were given to the patient in the appointment",
            required=True,
        ),
        "supplies": fields.List(
            fields.Nested(supply_sell_request),
            description="The supplies that were sold to the patient in the appointment",
            required=True,
        ),
    },
)

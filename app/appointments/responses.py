from flask_restx import fields
from app.extensions import api
from app.dentists.responses import dentist_response
from app.patients.responses import patient_response
from app.supplies.responses import supply_sells_response
from app.services.responses import service_sells_response


sell_appointment_response = api.model(
    "sell_response",
    {
        "id": fields.Integer(readonly=True, description="The id fo this sell"),
        "patient_id": fields.Integer(
            required=True,
            description="The id of the patient who this sell was created for",
        ),
        "appointment_id": fields.Integer(
            required=True,
            description="The id of the appointment in which the sell was created",
        ),
        "created_at": fields.DateTime(description="Creation date"),
        "paid_at": fields.DateTime(description="Payment date"),
        "subtotal": fields.Float(required=True, description="Subtotal amount"),
        "vat": fields.Float(required=True, description="VAT amount"),
        "total": fields.Float(required=True, description="Total amount"),
        "services": fields.List(
            fields.Nested(service_sells_response),
            description="List of services in the sell",
        ),
        "supplies": fields.List(
            fields.Nested(supply_sells_response),
            description="List of supplies in the sell",
        ),
        "status": fields.String(description="Sell status"),
    },
)

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
            fields.Nested(
                sell_appointment_response, description="The sell generated in this appointment"
            )
        ),
        "status": fields.String(description="The status of this appointment")
    },
)

from flask_restx import fields
from app.extensions import api
from app.supplies.responses import supply_sells_response
from app.services.responses import service_sells_response
from app.patients.responses import patient_response
from app.appointments.responses import appointment_response

# Define an API model for the Sell model
sell_response = api.model(
    "sell_response",
    {
        "id": fields.Integer(readonly=True, description="The id fo this sell"),
        "patient_id": fields.Integer(
            required=True,
            description="The id of the patient who this sell was created for",
        ),
        "patient": fields.Nested(
            patient_response, "The patient who this sell was created for"
        ),
        "appointment_id": fields.Integer(
            required=True,
            description="The id of the appointment in which the sell was created",
        ),
        "appointment": fields.Nested(
            appointment_response,
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

# Assuming you already have a service_model and sell_supplies_model defined
# The service_model and sell_supplies_model should be created similarly to the previous examples for their respective models.

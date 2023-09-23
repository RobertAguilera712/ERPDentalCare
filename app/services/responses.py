from flask_restx import fields
from app.extensions import api
from app.supplies.responses import supply_response

service_supplies_response = api.model("service_supplies_response", {
    ""
})

service_response = api.model(
    "service_response",
    {
        "id": fields.Integer(description="Unique identifier for the user"),
        "name": fields.String(
            description="The name of th service",
        ),
        "price": fields.Float(description="The price of the service"),
        "supplies": fields.List(
            fields.Nested(supply_response),
            description="The supplies that are used in this service.",
        ),
    },
)

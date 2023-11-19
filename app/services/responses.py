from flask_restx import fields
from app.extensions import api
from app.supplies.responses import supply_response

service_supplies_response = api.model(
    "service_supplies_response",
    {
        "id": fields.Integer(description="Unique identifier for this register"),
        "quantity": fields.Float(description="The quantity in which the supply is used for this service"),
        "supply": fields.Nested(supply_response, description="The supply that is used in this service")
    },
)

service_response = api.model(
    "service_response",
    {
        "id": fields.Integer(description="Unique identifier for the service"),
        "name": fields.String(
            description="The name of th service",
        ),
        "price": fields.Float(description="The price of the service"),
        "supplies": fields.List(
            fields.Nested(service_supplies_response),
            description="The supplies that are used in this service.",
        ),
        "cost": fields.Float(description="The cost of the service"),
    },
)

service_sells_response = api.model(
    "service_sells_response",
    {
        "id": fields.Integer(description="The id of this register"),
        "sell_id": fields.Integer(
            description="The id of sell in which the supply was sold"
        ),
        "service_id": fields.Integer(description="The id of the service that was sold"),
        "service": fields.Nested(service_response),
        "quantity": fields.Integer(description="The quantity that was sold"),
        "price": fields.Float(
            description="The unit price in which each service was sold"
        ),
        "subtotal": fields.Float(description="The subtotal of this sell"),
        "vat": fields.Float(description="The vat of this sell"),
        "total": fields.Float(description="The total of this sell"),
    },
)

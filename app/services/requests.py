from flask_restx import fields
from app.extensions import api

service_supply_request = api.model(
    "service_supply_request",
    {
        "supply_id": fields.Integer(required=True, description="The id of the supply that is used in this service"),
        "quantity": fields.Float(required=True, description="The amount of the supply that is used for this service. This amount needs to be in use quantity")
    }
)

service_request = api.model(
    "service_request",
    {
        "name": fields.String(
            required=True, description="The name of th service", max_length=80
        ),
        "price": fields.Float(required=True, description="The price of the service"),
        "supplies": fields.List(fields.Nested(service_supply_request), required=True, description="The supplies that are used in this service."),
    },
)



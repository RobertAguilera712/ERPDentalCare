from flask_restx import fields
from app.extensions import api

supply_request = api.model(
    "supply_request",
    {
        "name": fields.String(
            required=True, description="The name of th supply", max_length=60
        ),
        "cost": fields.Float(required=True, description="The cost of the supply"),
        "price": fields.Float(required=True, description="The price of the supply"),
        "is_salable": fields.Boolean(
            required=True,
            description="Whether the supply is salable as a product or not",
        ),
        "buy_unit": fields.String(
            required=True,
            description="The unit in which the supply is bought. Example Kilogram",
            max_length=60,
        ),
        "use_unit": fields.String(
            required=True,
            description="The unit in which the supply used. Example gram",
            max_length=60,
        ),
        "equivalence": fields.Float(
            required=True,
            description="The equivalence between the buy unit and the use unit. Example: If your buy unit is kilogram and your use unit is gram this field must be 1000",
        ),
        "image": fields.String(
            description="The image of the supply encoded as base64 string"
        ),
    },
)


buy_supply_request = api.model(
    "buy_supply_request",
    {
        "supply_id": fields.Integer(
            required=True, description="The id of the supply we want to buy"
        ),
        "quantity": fields.Integer(
            required=True,
            description="The quantity of the supply that we are buying. It must be in buy unit",
            min=1,
        ),
        "expiration_date": fields.Date(
            description="The date in which these buys expire"
        )
    },
)

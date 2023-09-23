from flask_restx import fields
from app.extensions import api
from app.get.responses import tax_regime_response

supply_response = api.model(
    "supply_response",
    {
        "id": fields.Integer(description="Unique identifier for the user"),
        "name": fields.String(description="The name of th supply"),
        "cost": fields.Float(description="The cost of the supply"),
        "price": fields.Float(description="The price of the supply"),
        "is_salable": fields.Boolean(
            description="Whether the supply is salable as a product or not",
        ),
        "buy_unit": fields.String(
            description="The unit in which the supply is bought. Example Kilogram",
        ),
        "use_unit": fields.String(
            description="The unit in which the supply used. Example gram",
        ),
        "equivalence": fields.Float(
            description="The equivalence between the buy unit and the use unit. Example: If your buy unit is kilogram and your use unit is gram this field must be 1000",
        ),
        "image": fields.String(
            description="The image of the supply encoded as base64 string"
        ),
    },
)

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
        "stock": fields.Float(
            description="The stock that is available of this supply in the inventory",
        ),
        "stock_in_use_unit": fields.Float(
            description="The stock in use unit that is available of this supply in the inventory",
        ),
        "image": fields.String(
            description="The image of the supply encoded as base64 string"
        ),
    },
)

supply_buy_response = api.model(
    "supply_buy_response",
    {
        "id": fields.Integer(description="The id of this buy"),
        "buy_date": fields.DateTime(description="The date in which this buy was made"),
        "expiration_date": fields.DateTime(
            description="The date in which the supplies of this buy expire"
        ),
        "quantity": fields.Integer(description="The quantity that was bought"),
        "available_use_quantity": fields.Float(
            description="The quantity that remains in the warehouse"
        ),
        "unit_cost": fields.Float(
            description="The price in which we bought each supply"
        ),
        "supply_id": fields.Integer(description="The id of the supply tha was bought"),
    },
)

supply_sells_response = api.model(
    "supply_sells_response",
    {
        "id": fields.Integer(description="The id of this register"),
        "sell_id": fields.Integer(
            description="The id of sell in which the supply was sold"
        ),
        "supply_id": fields.Integer(description="The id of the supply that was sold"),
        "supply": fields.Nested(supply_response),
        "quantity": fields.Integer(description="The quantity that was sold"),
        "price": fields.Float(
            description="The unit price in which each supply was sold"
        ),
        "subtotal": fields.Float(description="The subtotal of this sell"),
        "vat": fields.Float(description="The vat of this sell"),
        "total": fields.Float(description="The total of this sell"),
    },
)

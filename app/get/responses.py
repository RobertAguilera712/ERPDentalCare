from flask_restx import fields
from app.extensions import api

tax_regime_response = api.model(
    "tax_regime_response",
    {
        "id": fields.Integer(description="Unique identifier for the tax regime"),
        "name": fields.String(description="Name of the tax regime"),
        "key": fields.String(description="Key of the tax regime"),
    },
)

weekday_response = api.model(
    "weekday_response",
    {
        "id": fields.Integer(description="Unique identifier for the weekday"),
        "name": fields.String(description="Name of the weekday"),
    },
)

frequency_response = api.model(
    "frequency_response",
    {
        "id": fields.Integer(description="Unique identifier for the frequency"),
        "name": fields.String(description="Name of the frequency"),
        "duration": fields.Integer(description="The duration in days of the frequency"),
    },
)

allergy_response = api.model(
    "allergy_response",
    {
        "id": fields.Integer(description="Unique identifier for the allergy"),
        "name": fields.String(description="Name of the allergy"),
    },
)

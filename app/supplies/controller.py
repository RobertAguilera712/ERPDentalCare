from flask_restx import Resource, Namespace
from app.models import Supply
from app.extensions import db
from .responses import supply_response
from .requests import supply_request


supplies_ns = Namespace("api")


@supplies_ns.route("/supplies")
class SupplyListAPI(Resource):
    @supplies_ns.marshal_list_with(supply_response)
    def get(self):
        return Supply.query.filter(Supply.status == 1).all()

    @supplies_ns.expect(supply_request)
    @supplies_ns.marshal_with(supply_response)
    def post(self):
        supply = Supply(**supplies_ns.payload)
        db.session.add(supply)
        db.session.commit()
        return supply, 201

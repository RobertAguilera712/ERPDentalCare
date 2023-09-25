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


@supplies_ns.route("/supplies/<int:id>")
class SupplyApi(Resource):

    @supplies_ns.marshal_with(supply_response)
    def get(self, id):
        supply = Supply.query.get_or_404(id)
        return supply

    @supplies_ns.expect(supply_request)
    @supplies_ns.marshal_with(supply_response)
    def put(self, id):
        supply = Supply.query.get_or_404(id)

        supply_dict = supplies_ns.payload

        for key, value in supply_dict.items():
            setattr(supply, key, value)

        db.session.commit()
        return supply, 201

    def delete(self, id):
        supply = Supply.query.get_or_404(id)
        supply.status = 0
        db.session.commit()
        return {}, 204

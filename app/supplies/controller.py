from flask_restx import Resource, Namespace, abort
from app.models import Supply, RowStatus, SupplyBuys, UserRole
from app.extensions import db, authorizations, role_required
from .responses import supply_response, supply_buy_response, supply_sells_response
from .requests import supply_request, buy_supply_request
from datetime import datetime
from flask_jwt_extended import jwt_required


supplies_ns = Namespace("api", authorizations=authorizations)


@supplies_ns.route("/supplies")
class SupplyListAPI(Resource):
    method_decorators = [jwt_required()]

    @supplies_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @supplies_ns.marshal_list_with(supply_response)
    def get(self):
        return Supply.query.filter(Supply.status == RowStatus.ACTIVO).all()

    @supplies_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @supplies_ns.expect(supply_request, validate=True)
    @supplies_ns.marshal_with(supply_response)
    def post(self):
        supply = Supply(**supplies_ns.payload)
        try:
            db.session.add(supply)
            db.session.commit()
            return supply, 201
        except Exception as ex:
            db.session.rollback()
            print(f"An error ocurred while creating the new supply {str(ex)}")
            abort(500, "Failed to create the new supply. Try again later")


@supplies_ns.route("/supplies/<int:id>")
class SupplyApi(Resource):
    method_decorators = [jwt_required()]

    @supplies_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @supplies_ns.marshal_with(supply_response)
    def get(self, id):
        supply = Supply.query.get_or_404(id)
        return supply

    @supplies_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @supplies_ns.expect(supply_request, validate=True)
    @supplies_ns.marshal_with(supply_response)
    def put(self, id):
        supply = Supply.query.get_or_404(id)

        supply_dict = supplies_ns.payload

        for key, value in supply_dict.items():
            setattr(supply, key, value)

        try:
            db.session.commit()
            return supply, 201
        except Exception as ex:
            db.session.rollback()
            print(f"Error while modifying the supply {str(ex)}")
            abort(500, "Failed tho edit the supply. Try again later")

    @supplies_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    def delete(self, id):
        supply = Supply.query.get_or_404(id)
        supply.status = RowStatus.INACTIVO
        db.session.commit()
        return {}, 204


@supplies_ns.route("/supplies/<int:id>/buys")
class SupplyBuysListApi(Resource):
    method_decorators = [jwt_required()]

    @supplies_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @supplies_ns.marshal_list_with(supply_buy_response)
    def get(self, id):
        supply = Supply.query.get_or_404(id)
        return supply.buy_records


@supplies_ns.route("/supplies/<int:id>/sells")
class SupplySellsListApi(Resource):
    method_decorators = [jwt_required()]

    @supplies_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @supplies_ns.marshal_list_with(supply_sells_response)
    def get(self, id):
        supply = Supply.query.get_or_404(id)
        return supply.sells


@supplies_ns.route("/supplies/<int:id>/inventory")
class SupplyInventoryApi(Resource):
    method_decorators = [jwt_required()]

    @supplies_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @supplies_ns.marshal_list_with(supply_buy_response)
    def get(self, id):
        supply = Supply.query.get_or_404(id)
        return supply.inventory


@supplies_ns.route("/supplies/buys")
class SupplyBuysApi(Resource):
    method_decorators = [jwt_required()]

    @supplies_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @supplies_ns.expect(buy_supply_request, validate=True)
    def post(self):
        request = supplies_ns.payload
        supply_id = request["supply_id"]
        supply = Supply.query.get_or_404(supply_id)
        quantity = request["quantity"]
        str_expiration_date = request.get("expiration_date")
        date_format = "%Y-%m-%d"
        expiration_date = (
            datetime.strptime(str_expiration_date, date_format)
            if str_expiration_date
            else None
        )
        available_use_quantity = quantity * supply.equivalence

        buy = SupplyBuys(
            expiration_date=expiration_date,
            quantity=quantity,
            available_use_quantity=available_use_quantity,
            unit_cost=supply.cost,
            supply_id=supply_id,
        )
        try:
            db.session.add(buy)
            db.session.commit()
            return {}, 204
        except Exception as ex:
            db.session.rollback()
            print(f"An error occurred while adding the supply buy {ex}")
            abort(500, "Failed to add the buy. Try again later")

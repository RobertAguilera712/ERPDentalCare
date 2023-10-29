from flask_restx import Resource, Namespace
from app.models import Sell, UserRole
from app.extensions import db, authorizations, role_required
from .responses import sell_response
from flask_jwt_extended import jwt_required


sells_ns = Namespace("api", authorizations=authorizations)


@sells_ns.route("/sells")
class SellsListAPI(Resource):
    method_decorators = [jwt_required()]
    @sells_ns.doc(security='jsonWebToken')
    @role_required([UserRole.ADMIN])
    @sells_ns.marshal_list_with(sell_response)
    def get(self):
        return Sell.query.all()

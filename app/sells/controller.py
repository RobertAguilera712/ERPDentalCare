from flask_restx import Resource, Namespace
from app.models import Sell, UserRole, SellStatus
from app.extensions import db, authorizations, role_required, parser
from .responses import sell_response
from flask_jwt_extended import jwt_required


sells_ns = Namespace("api", authorizations=authorizations)


@sells_ns.route("/sells")
class SellsListAPI(Resource):
    method_decorators = [jwt_required()]

    @sells_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @sells_ns.marshal_list_with(sell_response)
    @sells_ns.expect(parser)
    def get(self):
        args = parser.parse_args()
        status_param = args.get("status")
        status_param = status_param.upper() if status_param else None
        if status_param in SellStatus.__members__:
            status = SellStatus[status_param]
            return Sell.query.filter(Sell.status == status)
        return Sell.query.all()

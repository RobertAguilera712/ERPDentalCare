from flask_restx import Resource, Namespace, abort
from app.models import Service, ServiceSupplies, RowStatus, UserRole
from app.extensions import db, authorizations, role_required, parser
from .responses import service_response, service_sells_response
from .requests import service_request
from flask_jwt_extended import jwt_required


services_ns = Namespace("api", authorizations=authorizations)


@services_ns.route("/services")
class ServicesListAPI(Resource):
    method_decorators = [jwt_required()]

    @services_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN, UserRole.DENTIST])
    @services_ns.marshal_list_with(service_response)
    @services_ns.expect(parser)
    def get(self):
        args = parser.parse_args()
        status_param = args.get("status")
        status_param = status_param.upper() if status_param else None
        if status_param in RowStatus.__members__:
            status = RowStatus[status_param]
            return Service.query.filter(Service.status == status).all()
        return Service.query.all()

    @services_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN, UserRole.DENTIST])
    @services_ns.expect(service_request, validate=True)
    @services_ns.marshal_with(service_response)
    def post(self):
        service = Service(
            name=services_ns.payload["name"], price=services_ns.payload["price"]
        )

        supplies = []
        for supply in services_ns.payload["supplies"]:
            service_supply = ServiceSupplies(
                service_id=service.id,
                supply_id=supply["supply_id"],
                quantity=supply["quantity"],
            )
            db.session.add(service_supply)
            supplies.append(service_supply)

        service.supplies_query.extend(supplies)
        try:
            db.session.add(service)
            db.session.commit()
            return service, 201
        except Exception as ex:
            db.session.rollback()
            print(f"Error while creating the service {str(ex)}")
            abort(500, "Failed to create the service. Try again later")


@services_ns.route("/services/<int:id>/sells")
class SupplySellsListApi(Resource):
    method_decorators = [jwt_required()]

    @services_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @services_ns.marshal_list_with(service_sells_response)
    def get(self, id):
        service = Service.query.get_or_404(id)
        return service.sells


@services_ns.route("/services/<int:id>")
class ServicesApi(Resource):
    method_decorators = [jwt_required()]

    @services_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @services_ns.marshal_with(service_response)
    def get(self, id):
        service = Service.query.get_or_404(id)
        return service

    @services_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @services_ns.expect(service_request, validate=True)
    @services_ns.marshal_with(service_response)
    def put(self, id):
        service = Service.query.get_or_404(id)

        service_dict = services_ns.payload
        service.name = service_dict["name"]
        service.price = service_dict["price"]

        for supply in service.supplies_query:
            db.session.delete(supply)

        service.supplies_query = []

        supplies = []
        for supply in services_ns.payload["supplies"]:
            service_supply = ServiceSupplies(
                service_id=service.id,
                supply_id=supply["supply_id"],
                quantity=supply["quantity"],
            )
            db.session.add(service_supply)
            supplies.append(service_supply)

        service.supplies_query.extend(supplies)

        try:
            db.session.commit()
            return service, 201
        except Exception as ex:
            db.session.rollback()
            print(f"Error while modifying the service {str(ex)}")
            abort(500, "Failed to edit the service. Try again later")

    @services_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    def delete(self, id):
        service = Service.query.get_or_404(id)
        service.status = RowStatus.INACTIVO
        try:
            db.session.commit()
            return {}, 204
        except Exception as ex:
            db.session.rollback()
            print(f"Error while deleting the service {str(ex)}")
            abort(500, "Failed to delete the service. Try again later")

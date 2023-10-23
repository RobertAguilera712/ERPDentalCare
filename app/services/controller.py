from flask_restx import Resource, Namespace
from app.models import Service, ServiceSupplies, RowStatus
from app.extensions import db
from .responses import service_response
from .requests import service_request


services_ns = Namespace("api")


@services_ns.route("/services")
class ServicesListAPI(Resource):
    @services_ns.marshal_list_with(service_response)
    def get(self):
        return Service.query.filter(Service.status == RowStatus.ACTIVO).all()

    @services_ns.expect(service_request)
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
        db.session.add(service)
        db.session.commit()
        return service, 201


@services_ns.route("/services/<int:id>")
class ServicesApi(Resource):
    @services_ns.marshal_with(service_response)
    def get(self, id):
        service = Service.query.get_or_404(id)
        return service

    @services_ns.expect(service_request)
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

        db.session.commit()
        return service, 201

    def delete(self, id):
        service = Service.query.get_or_404(id)
        service.status = 0
        db.session.commit()
        return {}, 204

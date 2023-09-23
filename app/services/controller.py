from flask_restx import Resource, Namespace
from app.models import Service, ServiceSupplies
from app.extensions import db
from .responses import service_response
from .requests import service_request


services_ns = Namespace("api")


@services_ns.route("/services")
class ServicesListAPI(Resource):
    @services_ns.marshal_list_with(service_response)
    def get(self):
        return Service.query.filter(Service.status == 1).all()

    @services_ns.expect(service_request)
    @services_ns.marshal_with(service_response)
    def post(self):
        service = Service(name=services_ns.payload['name'], price=services_ns.payload['price'])

        supplies = []
        for supply in services_ns.payload['supplies']:
            service_supply = ServiceSupplies(service_id = service.id,
                                            supply_id = supply['supply_id'],
                                            quantity= supply['quantity'])
            db.session.add(service_supply)
            supplies.append(service_supply)

        service.supplies_query.extend(supplies)
        db.session.add(service)
        db.session.commit()
        return service, 201
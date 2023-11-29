from flask_restx import Resource, Namespace, abort
from app.models import Allergy, RowStatus, UserRole
from app.extensions import db, authorizations, role_required, parser
from .responses import allergy_response
from .requests import allergy_request
from flask_jwt_extended import jwt_required


allergies_ns = Namespace("api", authorizations=authorizations)


@allergies_ns.route("/allergies")
class AllergiesListAPI(Resource):
    method_decorators = [jwt_required()]

    @allergies_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN, UserRole.DENTIST, UserRole.PATIENT])
    @allergies_ns.marshal_list_with(allergy_response)
    @allergies_ns.expect(parser)
    def get(self):
        args = parser.parse_args()
        status_param = args.get("status")
        status_param = status_param.upper() if status_param else None
        if status_param in RowStatus.__members__:
            status = RowStatus[status_param]
            return Allergy.query.filter(Allergy.status == status).all()
        return Allergy.query.all()

    @allergies_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN, UserRole.DENTIST])
    @allergies_ns.expect(allergy_request, validate=True)
    @allergies_ns.marshal_with(allergy_response, code=201)
    def post(self):
        name = allergies_ns.payload["name"]
        existing_allergy = Allergy.query.filter(Allergy.status == RowStatus.ACTIVO, Allergy.name == name).first()

        if existing_allergy:
            abort(400, "An allergy with the same name already exists")

        allergy = Allergy(name=name)

        try:
            db.session.add(allergy)
            db.session.commit()
            return allergy, 201
        except Exception as ex:
            db.session.rollback()
            print(f"Error while creating the allergy")
            abort(500, "Failed to create the allergy. Try again later")

@allergies_ns.route("/allergies/<int:id>")
class allergiesApi(Resource):
    method_decorators = [jwt_required()]

    @allergies_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @allergies_ns.marshal_with(allergy_response)
    def get(self, id):
        allergy = Allergy.query.get_or_404(id)
        return allergy

    @allergies_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @allergies_ns.expect(allergy_request, validate=True)
    @allergies_ns.marshal_with(allergy_response)
    def put(self, id):
        allergy = Allergy.query.get_or_404(id)

        name = allergies_ns.payload["name"]
        existing_allergy = Allergy.query.filter(Allergy.id != allergy.id, Allergy.status == RowStatus.ACTIVO, Allergy.name == name).first()

        if existing_allergy:
            abort(400, "An allergy with the same name already exists")

        allergy.name = name

        try:
            db.session.commit()
            return allergy, 201
        except Exception as ex:
            db.session.rollback()
            print(f"Error while modifying the allergy {str(ex)}")
            abort(500, "Failed to modify the allergy. Try again later")


    @allergies_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    def delete(self, id):
        allergy = Allergy.query.get_or_404(id)
        allergy.status = RowStatus.INACTIVO
        try:
            db.session.commit()
            return {}, 204
        except Exception as ex:
            db.session.rollback()
            print(f"Error while deleting the allergy {str(ex)}")
            abort(500, "Failed to delete the allergy. Try again later")

from flask_restx import Resource, Namespace
from app.models import TaxRegime, Weekday, Frequency, Allergy, RowStatus, UserRole
from app.extensions import db, authorizations, role_required
from .responses import *
from flask_jwt_extended import jwt_required, current_user


get_ns = Namespace("api/get", authorizations=authorizations)


@get_ns.route("/tax-regime")
class TaxRegimeListAPI(Resource):
    method_decorators = [jwt_required()]

    @get_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @get_ns.marshal_list_with(tax_regime_response)
    def get(self):
        return TaxRegime.query.filter(TaxRegime.status == RowStatus.ACTIVO).all()


@get_ns.route("/weekdays")
class WeekdayListAPI(Resource):
    method_decorators = [jwt_required()]

    @get_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @get_ns.marshal_list_with(weekday_response)
    def get(self):
        return Weekday.query.filter(Weekday.status == RowStatus.ACTIVO).all()


@get_ns.route("/frequencies")
class FrequenciesListAPI(Resource):
    method_decorators = [jwt_required()]

    @get_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @get_ns.marshal_list_with(frequency_response)
    def get(self):
        return Frequency.query.filter(Frequency.status == RowStatus.ACTIVO).all()


@get_ns.route("/allergies")
class AllergiesListAPI(Resource):
    method_decorators = [jwt_required()]

    @get_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN, UserRole.PATIENT])
    @get_ns.marshal_list_with(allergy_response)
    def get(self):
        return Allergy.query.filter(Allergy.status == RowStatus.ACTIVO).all()

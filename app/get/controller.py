from flask_restx import Resource, Namespace
from app.models import TaxRegime, Weekday, Frequency, Allergy
from app.extensions import db
from .responses import *


get_ns = Namespace("api/get")


@get_ns.route("/tax-regime")
class TaxRegimeListAPI(Resource):
    @get_ns.marshal_list_with(tax_regime_response)
    def get(self):
        return TaxRegime.query.filter(TaxRegime.status == 1).all()


@get_ns.route("/weekdays")
class WeekdayListAPI(Resource):
    @get_ns.marshal_list_with(weekday_response)
    def get(self):
        return Weekday.query.filter(Weekday.status == 1).all()


@get_ns.route("/frequencies")
class FrequenciesListAPI(Resource):
    @get_ns.marshal_list_with(frequency_response)
    def get(self):
        return Frequency.query.filter(Frequency.status == 1).all()


@get_ns.route("/allergies")
class AllergiesListAPI(Resource):
    @get_ns.marshal_list_with(allergy_response)
    def get(self):
        return Allergy.query.filter(Allergy.status == 1).all()
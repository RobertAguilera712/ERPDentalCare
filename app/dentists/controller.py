from flask_restx import Resource, Namespace
from app.models import Person, User, Dentist, Weekday, Diploma
from app.extensions import db
from .responses import dentist_response
from .requests import dentist_request
import datetime


dentists_ns = Namespace("api")


@dentists_ns.route("/dentists")
class PatientsListAPI(Resource):
    @dentists_ns.marshal_list_with(dentist_response)
    def get(self):
        return Dentist.query.filter(Dentist.status == 1).all()

    @dentists_ns.expect(dentist_request)
    @dentists_ns.marshal_with(dentist_response)
    def post(self):
        person_request = dentists_ns.payload["person"]
        user_request = dentists_ns.payload["user"]
        person = Person(**person_request)
        db.session.add(person)
        user = User(**user_request)
        db.session.add(user)
        dentist = Dentist(user=user, person=person)
        dentist.professional_license = dentists_ns.payload["professional_license"]
        dentist.hired_at = dentists_ns.payload["hired_at"]
        dentist.position = dentists_ns.payload["position"]
        selected_weekdays = Weekday.query.filter(Weekday.id.in_(dentists_ns.payload["weekdays"])).all()
        dentist.weekdays.extend(selected_weekdays)

        start_hour = dentists_ns.payload["start_hour"]
        start_minute = dentists_ns.payload["start_minute"]
        end_hour = dentists_ns.payload["end_hour"]
        end_minute = dentists_ns.payload["end_minute"]
        dentist.start_time = datetime.time(start_hour, start_minute, 0)
        dentist.end_time = datetime.time(end_hour, end_minute, 0)
        dentist.frequency_id = dentists_ns.payload["frequency_id"]

        diplomas = []
        for diploma_request in dentists_ns.payload["diplomas"]:
            diploma = Diploma(name=diploma_request['name'], university=diploma_request['university'])
            db.session.add(diploma)
            diplomas.append(diploma)

        dentist.diplomas.extend(diplomas)

        db.session.add(dentist)
        db.session.commit()
        return dentist, 201

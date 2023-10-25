from flask_restx import Resource, Namespace, abort
from app.models import Person, User, Dentist, Weekday, Diploma, RowStatus
from app.extensions import db
from .responses import dentist_response
from .requests import dentist_request
import datetime


dentists_ns = Namespace("api")


@dentists_ns.route("/dentists")
class DentistListAPI(Resource):
    @dentists_ns.marshal_list_with(dentist_response)
    def get(self):
        return Dentist.query.filter(Dentist.status == RowStatus.ACTIVO).all()

    @dentists_ns.expect(dentist_request, validate=True)
    @dentists_ns.marshal_with(dentist_response)
    def post(self):
        person_request = dentists_ns.payload["person"]
        user_request = dentists_ns.payload["user"]
        person = Person(**person_request)

        existing_user = User.query.filter(User.email == user_request["email"]).first()
        if existing_user:
            abort(400, "A user with the same email already exists.")

        user = User(**user_request)

        dentist = Dentist(user=user, person=person)
        dentist.professional_license = dentists_ns.payload["professional_license"]
        dentist.hired_at = dentists_ns.payload["hired_at"]
        dentist.position = dentists_ns.payload["position"]
        selected_weekdays = Weekday.query.filter(
            Weekday.id.in_(dentists_ns.payload["weekdays"])
        ).all()
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
            diploma = Diploma(
                name=diploma_request["name"], university=diploma_request["university"]
            )
            diplomas.append(diploma)

        dentist.diplomas.extend(diplomas)

        try:
            db.session.add(dentist)
            db.session.commit()
            return dentist, 201
        except Exception as e:
            db.session.rollback()
            print(f"Error creating dentist: {str(e)}")
            abort(500, "Failed to create the dentist. Please try again later.")


@dentists_ns.route("/dentists/<int:id>")
class DentistApi(Resource):
    @dentists_ns.marshal_with(dentist_response)
    def get(self, id):
        dentist = Dentist.query.get_or_404(id)
        return dentist

    @dentists_ns.expect(dentist_request, validate=True)
    @dentists_ns.marshal_with(dentist_response)
    def put(self, id):
        dentist = Dentist.query.get_or_404(id)

        person_dict = dentists_ns.payload["person"]
        user_dict = dentists_ns.payload["user"]

        for key, value in person_dict.items():
            setattr(dentist.person, key, value)

        same_email = dentist.user.email == user_dict["email"]

        existing_user = (
            False
            if same_email
            else User.query.filter(User.email == user_dict["email"]).first()
        )
        if existing_user:
            abort(400, "A user with the same email already exists.")

        for key, value in user_dict.items():
            setattr(dentist.user, key, value)

        dentist.professional_license = dentists_ns.payload["professional_license"]
        dentist.hired_at = dentists_ns.payload["hired_at"]
        dentist.position = dentists_ns.payload["position"]
        selected_weekdays = Weekday.query.filter(
            Weekday.id.in_(dentists_ns.payload["weekdays"])
        ).all()
        dentist.weekdays = []
        dentist.weekdays.extend(selected_weekdays)

        start_hour = dentists_ns.payload["start_hour"]
        start_minute = dentists_ns.payload["start_minute"]
        end_hour = dentists_ns.payload["end_hour"]
        end_minute = dentists_ns.payload["end_minute"]
        dentist.start_time = datetime.time(start_hour, start_minute, 0)
        dentist.end_time = datetime.time(end_hour, end_minute, 0)
        dentist.frequency_id = dentists_ns.payload["frequency_id"]

        dentist.diplomas = []
        diplomas = []
        for diploma_request in dentists_ns.payload["diplomas"]:
            diploma = Diploma(
                name=diploma_request["name"], university=diploma_request["university"]
            )
            diplomas.append(diploma)

        dentist.diplomas.extend(diplomas)

        try:
            db.session.commit()
            return dentist, 201
        except Exception as e:
            db.session.rollback()
            print(f"Error updating dentist: {str(e)}")
            abort(500, "Failed to update the dentist. Please try again later.")

    def delete(self, id):
        dentist = Dentist.query.get_or_404(id)
        dentist.status = 0
        db.session.commit()
        return {}, 204

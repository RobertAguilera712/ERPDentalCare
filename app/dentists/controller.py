from flask_restx import Resource, Namespace, abort
from app.models import (
    Person,
    User,
    Dentist,
    Weekday,
    Diploma,
    RowStatus,
    UserRole,
    Appointment,
    AppointmentStatus,
)
from app.extensions import db, authorizations, bcrypt, role_required, parser
from app.appointments.responses import appointment_response
from .responses import dentist_response
from .requests import dentist_request, edit_dentist_request
from flask_jwt_extended import (
    jwt_required,
    current_user,
)
import datetime


dentists_ns = Namespace("api", authorizations=authorizations)


@dentists_ns.route("/dentists")
class DentistListAPI(Resource):
    method_decorators = [jwt_required()]

    @dentists_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @dentists_ns.marshal_list_with(dentist_response)
    @dentists_ns.expect(parser)
    def get(self):
        args = parser.parse_args()
        status_param = args.get("status")
        status_param = status_param.upper() if status_param else None
        if status_param in RowStatus.__members__:
            status = RowStatus[status_param]
            return Dentist.query.filter(Dentist.status == status).all()
        return Dentist.query.all()

    @dentists_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @dentists_ns.expect(dentist_request, validate=True)
    @dentists_ns.marshal_with(dentist_response)
    def post(self):
        person_request = dentists_ns.payload["person"]
        user_request = dentists_ns.payload["user"]
        person = Person(**person_request)

        existing_user = User.query.filter(User.email == user_request["email"]).first()
        if existing_user:
            abort(400, "A user with the same email already exists.")

        user = User()
        user.email = user_request["email"]
        user.image = user_request["image"]
        hashed_password = bcrypt.generate_password_hash(
            user_request["password"]
        ).decode("utf-8")
        user.password = hashed_password
        user.role = UserRole.DENTIST

        dentist = Dentist(user=user, person=person)
        dentist.professional_license = dentists_ns.payload["professional_license"]
        dentist.hired_at = dentists_ns.payload["hired_at"]
        dentist.position = dentists_ns.payload["position"]
        # selected_weekdays = Weekday.query.filter(
        #     Weekday.id.in_(dentists_ns.payload["weekdays"])
        # ).all()
        # dentist.weekdays.extend(selected_weekdays)

        # start_hour = dentists_ns.payload["start_hour"]
        # start_minute = dentists_ns.payload["start_minute"]
        # end_hour = dentists_ns.payload["end_hour"]
        # end_minute = dentists_ns.payload["end_minute"]
        dentist.start_time = datetime.time(12, 0, 0)
        dentist.end_time = datetime.time(12, 0, 0)
        dentist.frequency_id = 1

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


@dentists_ns.route("/dentists/<int:id>/appointments")
class DentistAppointment(Resource):
    method_decorators = [jwt_required()]

    @dentists_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @dentists_ns.marshal_with(appointment_response)
    def get(self, id):
        dentist = Dentist.query.filter(
            Dentist.id == id, Dentist.status == RowStatus.ACTIVO
        ).first()
        if not dentist:
            abort(404, "The dentist does not exists")
        return dentist.appointments_query.filter(
            Appointment.end_date > datetime.datetime.now()
        ).all()


@dentists_ns.route("/dentists/<int:id>/record")
class DentistRecord(Resource):
    method_decorators = [jwt_required()]

    @dentists_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @dentists_ns.marshal_with(appointment_response)
    def get(self, id):
        dentist = Dentist.query.filter(
            Dentist.id == id, Dentist.status == RowStatus.ACTIVO
        ).first()
        if not dentist:
            abort(404, "The dentist does not exists")
        return dentist.appointments_query.filter(
            Appointment.end_date < datetime.datetime.now(),
            Appointment.status == AppointmentStatus.ATENDIDA,
        ).all()


@dentists_ns.route("/dentists/my/appointments")
class DentistMyAppointment(Resource):
    method_decorators = [jwt_required()]

    @dentists_ns.doc(security="jsonWebToken")
    @role_required([UserRole.DENTIST])
    @dentists_ns.marshal_with(appointment_response)
    def get(self):
        dentist = Dentist.query.filter(Dentist.user == current_user).first()
        if not dentist:
            abort(404, "The dentist does not exists")
        return dentist.appointments_query.filter(
            Appointment.end_date > datetime.datetime.now()
        ).all()


@dentists_ns.route("/dentists/my/record")
class DentistMyRecord(Resource):
    method_decorators = [jwt_required()]

    @dentists_ns.doc(security="jsonWebToken")
    @role_required([UserRole.DENTIST])
    @dentists_ns.marshal_with(appointment_response)
    def get(self):
        dentist = Dentist.query.filter(Dentist.user == current_user).first()
        if not dentist:
            abort(404, "The dentist does not exists")
        return dentist.appointments_query.filter(
            Appointment.end_date < datetime.datetime.now(),
            Appointment.status == AppointmentStatus.ATENDIDA,
        ).all()


@dentists_ns.route("/dentists/me")
class DentistMe(Resource):
    method_decorators = [jwt_required()]

    @dentists_ns.doc(security="jsonWebToken")
    @role_required([UserRole.DENTIST])
    @dentists_ns.marshal_with(dentist_response)
    def get(self):
        dentist = Dentist.query.filter(Dentist.user == current_user).first()
        if not dentist:
            abort(404, "The dentist does not exists")
        return dentist

    @dentists_ns.doc(security="jsonWebToken")
    @role_required([UserRole.DENTIST])
    @dentists_ns.expect(edit_dentist_request, validate=True)
    @dentists_ns.marshal_with(dentist_response)
    def put(self):
        dentist = Dentist.query.filter(Dentist.user == current_user).first()

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


@dentists_ns.route("/dentists/<int:id>")
class DentistApi(Resource):
    method_decorators = [jwt_required()]

    @dentists_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @dentists_ns.marshal_with(dentist_response)
    def get(self, id):
        dentist = Dentist.query.get_or_404(id)
        return dentist

    @dentists_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @dentists_ns.expect(edit_dentist_request, validate=True)
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

    @dentists_ns.doc(security="jsonWebToken")
    @dentists_ns.marshal_with(dentist_response)
    @role_required([UserRole.ADMIN])
    def delete(self, id):
        dentist = Dentist.query.get_or_404(id)
        dentist.status = RowStatus.INACTIVO
        db.session.commit()
        return dentist

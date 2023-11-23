from flask_restx import Resource, Namespace, abort
from app.models import (
    Person,
    User,
    Patient,
    Allergy,
    RowStatus,
    UserRole,
    Appointment,
    AppointmentStatus,
)
from app.extensions import db, bcrypt, authorizations, role_required, parser
from app.appointments.responses import appointment_response
from app.sells.responses import sell_response
from .responses import patient_response
from .requests import patient_request, edit_patient_request
from flask_jwt_extended import (
    jwt_required,
    current_user,
)
from datetime import datetime


patients_ns = Namespace("api", authorizations=authorizations)


@patients_ns.route("/patients")
class PatientsListAPI(Resource):
    method_decorators = [jwt_required()]

    @patients_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @patients_ns.marshal_list_with(patient_response)
    @patients_ns.expect(parser)
    def get(self):
        args = parser.parse_args()
        status_param = args.get("status")
        status_param = status_param.upper() if status_param else None
        if status_param in RowStatus.__members__:
            status = RowStatus[status_param]
            return Patient.query.filter(Patient.status == status).all()
        return Patient.query.all()

    @patients_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @patients_ns.expect(patient_request, validate=True)
    @patients_ns.marshal_with(patient_response)
    def post(self):
        person_request = patients_ns.payload["person"]
        user_request = patients_ns.payload["user"]
        allergies_ids = [
            allergy["id"]
            for allergy in patients_ns.payload["allergies"]
            if allergy["id"] != 0
        ]
        selected_allergies = Allergy.query.filter(Allergy.id.in_(allergies_ids)).all()

        allergies_names = [
            allergy["name"]
            for allergy in patients_ns.payload["allergies"]
            if allergy["id"] == 0
        ]
        for name in allergies_names:
            allergy = Allergy(name=name)
            selected_allergies.append(allergy)

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
        user.role = UserRole.PATIENT

        patient = Patient(user=user, person=person)
        patient.allergies.extend(selected_allergies)

        try:
            db.session.add(patient)
            db.session.commit()
            return patient, 201
        except Exception as e:
            db.session.rollback()
            print(f"Error creating patient: {str(e)}")
            abort(500, "Failed to create the patient. Please try again later.")


@patients_ns.route("/patients/<int:id>")
class PatientsApi(Resource):
    method_decorators = [jwt_required()]

    @patients_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @patients_ns.marshal_with(patient_response)
    def get(self, id):
        patient = Patient.query.get_or_404(id)
        return patient

    @patients_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @patients_ns.expect(edit_patient_request, validate=True)
    @patients_ns.marshal_with(patient_response)
    def put(self, id):
        patient = Patient.query.get_or_404(id)

        person_dict = patients_ns.payload["person"]
        user_dict = patients_ns.payload["user"]

        for key, value in person_dict.items():
            setattr(patient.person, key, value)

        same_email = patient.user.email == user_dict["email"]

        existing_user = (
            False
            if same_email
            else User.query.filter(User.email == user_dict["email"]).first()
        )
        if existing_user:
            abort(400, "A user with the same email already exists.")

        for key, value in user_dict.items():
            setattr(patient.user, key, value)

        allergies_ids = [
            allergy["id"]
            for allergy in patients_ns.payload["allergies"]
            if allergy["id"] != 0
        ]
        selected_allergies = Allergy.query.filter(Allergy.id.in_(allergies_ids)).all()

        allergies_names = [
            allergy["name"]
            for allergy in patients_ns.payload["allergies"]
            if allergy["id"] == 0
        ]
        for name in allergies_names:
            allergy = Allergy(name=name)
            selected_allergies.append(allergy)

        patient.allergies = []
        patient.allergies.extend(selected_allergies)

        db.session.commit()
        return patient, 201

    @patients_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    def delete(self, id):
        patient = Patient.query.get_or_404(id)
        patient.status = RowStatus.INACTIVO
        db.session.commit()
        return {}, 204


@patients_ns.route("/patients/<int:id>/appointments")
class PatientAppointments(Resource):
    method_decorators = [jwt_required()]

    @patients_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @patients_ns.marshal_with(appointment_response)
    def get(self, id):
        patient = Patient.query.filter(
            Patient.id == id, Patient.status == RowStatus.ACTIVO
        ).first()
        if not patient:
            abort(404, "The patient does not exist")
        return patient.appointments_query.filter(
            Appointment.end_date > datetime.now()
        ).all()


@patients_ns.route("/patients/<int:id>/record")
class PatientRecord(Resource):
    method_decorators = [jwt_required()]

    @patients_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @patients_ns.marshal_with(appointment_response)
    def get(self, id):
        patient = Patient.query.filter(
            Patient.id == id, Patient.status == RowStatus.ACTIVO
        ).first()
        if not patient:
            abort(404, "The patient does not exist")
        return patient.appointments_query.filter(
            Appointment.end_date < datetime.now(),
            Appointment.status == AppointmentStatus.ATENDIDA,
        ).all()


@patients_ns.route("/patients/my/record")
class PatientMyRecord(Resource):
    method_decorators = [jwt_required()]

    @patients_ns.doc(security="jsonWebToken")
    @role_required([UserRole.PATIENT])
    @patients_ns.marshal_with(appointment_response)
    def get(self):
        patient = Patient.query.filter(Patient.user == current_user).first()
        if not patient:
            abort(404, "The dentist does not exists")
        return patient.appointments_query.filter(
            Appointment.end_date < datetime.now(),
            Appointment.status == AppointmentStatus.ATENDIDA,
        ).all()


@patients_ns.route("/patients/my/appointments")
class PatientMyAppointments(Resource):
    method_decorators = [jwt_required()]

    @patients_ns.doc(security="jsonWebToken")
    @role_required([UserRole.PATIENT])
    @patients_ns.marshal_with(appointment_response)
    def get(self):
        patient = Patient.query.filter(Patient.user == current_user).first()
        if not patient:
            abort(404, "The dentist does not exists")
        return patient.appointments_query.filter(
            Appointment.end_date > datetime.now()
        ).all()


@patients_ns.route("/patients/my/sells")
class PatientMySells(Resource):
    method_decorators = [jwt_required()]

    @patients_ns.doc(security="jsonWebToken")
    @role_required([UserRole.PATIENT])
    @patients_ns.marshal_with(sell_response)
    def get(self):
        patient = Patient.query.filter(Patient.user == current_user).first()
        if not patient:
            abort(404, "The patient does not exists")
        return patient.sells


@patients_ns.route("/patients/me")
class PatientMySells(Resource):
    method_decorators = [jwt_required()]

    @patients_ns.doc(security="jsonWebToken")
    @role_required([UserRole.PATIENT])
    @patients_ns.marshal_with(patient_response)
    def get(self):
        patient = Patient.query.filter(Patient.user == current_user).first()
        if not patient:
            abort(404, "The patient does not exists")
        return patient

    @patients_ns.doc(security="jsonWebToken")
    @role_required([UserRole.PATIENT])
    @patients_ns.marshal_with(patient_response)
    @patients_ns.expect(edit_patient_request, validate=True)
    def put(self):
        patient = Patient.query.filter(Patient.user == current_user).first()

        person_dict = patients_ns.payload["person"]
        user_dict = patients_ns.payload["user"]

        for key, value in person_dict.items():
            setattr(patient.person, key, value)

        same_email = patient.user.email == user_dict["email"]

        existing_user = (
            False
            if same_email
            else User.query.filter(User.email == user_dict["email"]).first()
        )
        if existing_user:
            abort(400, "A user with the same email already exists.")

        for key, value in user_dict.items():
            setattr(patient.user, key, value)

        allergies_ids = [
            allergy["id"]
            for allergy in patients_ns.payload["allergies"]
            if allergy["id"] != 0
        ]
        selected_allergies = Allergy.query.filter(Allergy.id.in_(allergies_ids)).all()

        allergies_names = [
            allergy["name"]
            for allergy in patients_ns.payload["allergies"]
            if allergy["id"] == 0
        ]
        for name in allergies_names:
            allergy = Allergy(name=name)
            selected_allergies.append(allergy)

        patient.allergies = []
        patient.allergies.extend(selected_allergies)

        db.session.commit()
        return patient, 201

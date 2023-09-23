from flask_restx import Resource, Namespace
from app.models import Person, User, Patient, Allergy
from app.extensions import db
from .responses import patient_response
from .requests import patient_request


patients_ns = Namespace("api")


@patients_ns.route("/patients")
class PatientsListAPI(Resource):
    @patients_ns.marshal_list_with(patient_response)
    def get(self):
        return Patient.query.filter(Patient.status == 1).all()

    @patients_ns.expect(patient_request)
    @patients_ns.marshal_with(patient_response)
    def post(self):
        person_request = patients_ns.payload["person"]
        user_request = patients_ns.payload["user"]
        allergies_ids = [ allergy['id'] for allergy in patients_ns.payload["allergies"] if allergy['id'] != 0]
        selected_allergies = Allergy.query.filter(Allergy.id.in_(allergies_ids)).all()

        allergies_names = [allergy['name'] for allergy in patients_ns.payload["allergies"] if allergy['id'] == 0]
        for name in allergies_names:
            allergy = Allergy(name=name)
            db.session.add(allergy)
            selected_allergies.append(allergy)


        person = Person(**person_request)
        db.session.add(person)
        user = User(**user_request)
        db.session.add(user)
        patient = Patient(user=user, person=person)
        patient.allergies.extend(selected_allergies)
        db.session.add(patient)
        db.session.commit()
        return patient, 201

@patients_ns.route("/patients/<int:id>")
class PatientsApi(Resource):
    @patients_ns.marshal_with(patient_response)
    def get(self, id):
        patient = Patient.query.get_or_404(id)
        return patient


    @patients_ns.expect(patient_request)
    @patients_ns.marshal_with(patient_response)
    def put(self, id):
        patient = Patient.query.get_or_404(id)

        person_dict = patients_ns.payload['person']
        for key, value in person_dict.items():
            setattr(patient.person, key, value)

        user_dict = patients_ns.payload['user']
        for key, value in user_dict.items():
            setattr(patient.user, key, value)

        allergies_ids = [ allergy['id'] for allergy in patients_ns.payload["allergies"] if allergy['id'] != 0]
        selected_allergies = Allergy.query.filter(Allergy.id.in_(allergies_ids)).all()

        allergies_names = [allergy['name'] for allergy in patients_ns.payload["allergies"] if allergy['id'] == 0]
        for name in allergies_names:
            allergy = Allergy(name=name)
            db.session.add(allergy)
            selected_allergies.append(allergy)

        patient.allergies = []
        patient.allergies.extend(selected_allergies)
        db.session.commit()
        return patient, 201


    def delete(self, id):
        patient = Patient.query.get_or_404(id)
        patient.status = 0
        db.session.commit()
        return {}, 204



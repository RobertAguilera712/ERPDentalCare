from flask_restx import Resource, Namespace, abort
from app.models import Appointment
from app.extensions import db
from .responses import appointment_response
from .requests import create_appointment_request
from datetime import datetime

appointments_ns = Namespace("api")


@appointments_ns.route("/appointment")
class AppointmentsAPI(Resource):
    @appointments_ns.expect(create_appointment_request, validate=True)
    @appointments_ns.marshal_with(appointment_response)
    def post(self):
        request = appointments_ns.payload

        date_format = "%Y-%m-%d"


        start_date = datetime.strptime(request["start_date"], date_format) 
        end_date = datetime.strptime(request["end_date"], date_format) 

        existing_appointment = Appointment.query.filter((Appointment.start_date == start_date) | (Appointment.end_date == end_date)).first()
        
        if (existing_appointment):
            abort(400, "An appointment with the same date already exists.")

        appointment = Appointment(**request)

        try:
            db.session.add(appointment)
            db.session.commit()
            return appointment, 201
        except Exception as e:
            # Handle other exceptions, log the error, and return a 500 Internal Server Error response
            db.session.rollback()
            print(f"Error creating appointment: {str(e)}")
            abort(500, "Failed to create the appointment. Please try again later.")



@appointments_ns.route("/appointment/<int:id>")
class AppointmentsListApi(Resource):
    @appointments_ns.marshal_with(appointment_response)
    def get(self, id):
        appointment = Appointment.query.get_or_404(id)
        return appointment

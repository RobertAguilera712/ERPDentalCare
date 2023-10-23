from flask_restx import Resource, Namespace
from app.models import Schedule, Appointment
from app.extensions import db
from .responses import appointment_response
from .requests import create_appointment_request

appointments_ns = Namespace("api")


@appointments_ns.route("/appointment")
class AppointmentsAPI(Resource):
    @appointments_ns.expect(create_appointment_request)
    @appointments_ns.marshal_with(appointment_response)
    def post(self):
        request = appointments_ns.payload

        selected_schedules = Schedule.query.filter(
            Schedule.id.in_(request["schedules"])
        ).all()
        selected_schedules.sort(key=lambda sc: sc.id)

        start_date = selected_schedules[0].start_date
        end_date = selected_schedules[-1].end_date

        appointment = Appointment(
            dentist_id=request["dentist_id"],
            patient_id=request["patient_id"],
            start_date=start_date,
            end_date=end_date,
        )
        appointment.schedules_query.extend(selected_schedules)

        db.session.add(appointment)
        db.session.commit()

        return appointment, 201

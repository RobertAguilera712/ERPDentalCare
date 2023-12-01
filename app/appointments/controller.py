from flask_restx import Resource, Namespace, abort
from app.models import (
    Appointment,
    Dentist,
    Patient,
    AppointmentStatus,
    Sell,
    SellServices,
    SellSupplies,
    Service,
    Supply,
    RowStatus,
    UserRole,
)
from app.extensions import db, authorizations, role_required, parser, onesignal_client, onesignal_app_id, onesignal_rest_api_key
from sqlalchemy import or_, and_
from flask_jwt_extended import jwt_required, current_user
from .responses import appointment_response
from .requests import (
    create_appointment_request,
    get_appointments_request,
    finish_appointment_request,
)
from datetime import datetime, timedelta
from onesignal_sdk.error import OneSignalHTTPError

appointments_ns = Namespace("api", authorizations=authorizations)


@appointments_ns.route("/appointment")
class AppointmentsAPI(Resource):
    method_decorators = [jwt_required()]

    @appointments_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @appointments_ns.expect(create_appointment_request, validate=True)
    @appointments_ns.marshal_with(appointment_response)
    def post(self):
        request = appointments_ns.payload

        start_date = datetime.fromisoformat(request["start_date"])
        end_date = datetime.fromisoformat(request["end_date"])

        existing_appointment = Appointment.query.filter(
            (
                and_(
                    Appointment.dentist_id == request["dentist_id"],
                    or_(
                        Appointment.start_date.between(start_date, end_date),
                        Appointment.end_date.between(start_date, end_date),
                    ),
                )
            )
        ).all()

        if len(existing_appointment) > 0:
            abort(400, "An appointment with the same date already exists.")

        dentist = Dentist.query.filter(
            Dentist.id == request["dentist_id"], Dentist.status == RowStatus.ACTIVO
        ).first()
        if not dentist:
            abort(400, "The specified dentist does not exist")

        patient = Patient.query.filter(
            Patient.id == request["patient_id"], Patient.status == RowStatus.ACTIVO
        ).first()
        if not patient:
            abort(400, "The specified patient does not exist")

        appointment = Appointment()
        appointment.start_date = start_date
        appointment.end_date = end_date
        appointment.dentist_id = dentist.id
        appointment.patient_id = patient.id

        try:
            db.session.add(appointment)
            db.session.commit()

            # Schedule notification for 10 minutes from now
            send_after = start_date - timedelta(days=1)
            send_after = send_after.replace(hour=12, minute=0, second=0, microsecond=0)


            message = f"Tienes una cita programada para el día {datetime.strftime(appointment.start_date, '%d/%m/%y')} a las {datetime.strftime(appointment.start_date, '%I:%M %p')}"
            user_id = appointment.patient.user.email
            notification = {
                'contents': {'en': message},
                "include_aliases": {
                    "external_id": [user_id]
                },
                "target_channel": "push",
                'send_after': send_after.isoformat(),
            }

            try:
                response = onesignal_client.send_notification(notification)
                print("___________________NOTIFICATION_________________________")
                print(response.body)
            except OneSignalHTTPError as e: # An exception is raised if response.status_code != 2xx
                print(e)
                print(e.status_code)
                print(e.http_response.json())
            return appointment, 200
        except Exception as e:
            # Handle other exceptions, log the error, and return a 500 Internal Server Error response
            db.session.rollback()
            print(f"Error creating appointment: {str(e)}")
            abort(500, "Failed to create the appointment. Please try again later.")


@appointments_ns.route("/appointment/list")
class AppointmentsListAllApi(Resource):
    method_decorators = [jwt_required()]

    @appointments_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @appointments_ns.marshal_list_with(appointment_response)
    @appointments_ns.expect(parser)
    def get(self):
        args = parser.parse_args()
        status_param = args.get("status")
        status_param = status_param.upper() if status_param else None
        if status_param in AppointmentStatus.__members__:
            status = AppointmentStatus[status_param]
            return Appointment.query.filter(Appointment.status == status).all()
        return Appointment.query.all()

    @appointments_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @appointments_ns.expect(get_appointments_request, validate=True)
    @appointments_ns.marshal_list_with(appointment_response)
    def post(self):
        request = appointments_ns.payload

        start_date = datetime.fromisoformat(request["start_date"])
        end_date = datetime.fromisoformat(request["end_date"])
        filter = and_(
            Appointment.start_date >= start_date, Appointment.end_date <= end_date
        )

        status = request.get("status")
        dentist_id = request.get("dentist_id")
        patient_id = request.get("patient_id")

        if status:
            status_filter = Appointment.status == AppointmentStatus[status]
            filter = and_(filter, status_filter)

        if dentist_id:
            dentist_filter = Appointment.dentist_id == dentist_id
            filter = and_(filter, dentist_filter)

        if patient_id:
            patient_filter = Appointment.patient_id == patient_id
            filter = and_(filter, patient_filter)

        return Appointment.query.filter(filter).all()


@appointments_ns.route("/appointment/<int:id>")
class AppointmentsListApi(Resource):
    method_decorators = [jwt_required()]

    @appointments_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @appointments_ns.marshal_with(appointment_response)
    def get(self, id):
        appointment = Appointment.query.get_or_404(id)
        return appointment

    @appointments_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @appointments_ns.expect(create_appointment_request, validate=True)
    @appointments_ns.marshal_with(appointment_response)
    def put(self, id):
        appointment = Appointment.query.get_or_404(id)

        request = appointments_ns.payload

        start_date = datetime.fromisoformat(request["start_date"])
        end_date = datetime.fromisoformat(request["end_date"])

        existing_appointment = Appointment.query.filter(
            (
                and_(
                    Appointment.id != id,
                    Appointment.dentist_id == request["dentist_id"],
                    or_(
                        Appointment.start_date.between(start_date, end_date),
                        Appointment.end_date.between(start_date, end_date),
                    ),
                )
            )
        ).all()

        if len(existing_appointment) > 0:
            abort(400, "An appointment with the same date already exists.")

        dentist = Dentist.query.filter(
            Dentist.id == request["dentist_id"], Dentist.status == RowStatus.ACTIVO
        ).first()
        if not dentist:
            abort(400, "The specified dentist does not exist")

        patient = Patient.query.filter(
            Patient.id == request["patient_id"], Patient.status == RowStatus.ACTIVO
        ).first()
        if not patient:
            abort(400, "The specified patient does not exist")

        appointment.start_date = start_date
        appointment.end_date = end_date
        appointment.dentist_id = dentist.id
        appointment.patient_id = patient.id

        try:
            db.session.commit()
            return appointment, 200
        except Exception as e:
            # Handle other exceptions, log the error, and return a 500 Internal Server Error response
            db.session.rollback()
            print(f"Error updating appointment: {str(e)}")
            abort(500, "Failed to update the appointment. Please try again later.")

    @appointments_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    @appointments_ns.marshal_with(appointment_response)
    def delete(self, id):
        appointment = Appointment.query.get_or_404(id)
        appointment.status = AppointmentStatus.CANCELADA
        try:
            db.session.commit()
            return appointment
        except Exception as ex:
            db.session.rollback()
            print(f"Error while updating the status of the appointment {str(ex)}")
            abort(500, "Failed to cancel the appointment. Try again later")


@appointments_ns.route("/appointment/<int:id>/notify")
class AppointmentsNotify(Resource):
    method_decorators = [jwt_required()]

    @appointments_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN])
    def get(self, id):
        appointment = Appointment.query.get_or_404(id)


        message = f"Tienes una cita programada para el día {datetime.strftime(appointment.start_date, '%d/%m/%y')} a las {datetime.strftime(appointment.start_date, '%I:%M %p')}"
        user_id = appointment.patient.user.email
        notification = {
            'contents': {'en': message},
            "include_aliases": {
                "external_id": [user_id]
            },
            "target_channel": "push"
        }

        try:
            response = onesignal_client.send_notification(notification)
            print(response.body)
            return {"message": "notification sent successfully"}, 200
        except OneSignalHTTPError as e: # An exception is raised if response.status_code != 2xx
            print(e)
            print(e.status_code)
            print(e.http_response.json())
            abort(500, "There was an error while sending the notification. Try again later")



@appointments_ns.route("/appointment/<int:id>/finish")
class AppointmentsFinish(Resource):
    method_decorators = [jwt_required()]

    @appointments_ns.doc(security="jsonWebToken")
    @role_required([UserRole.ADMIN, UserRole.DENTIST])
    @appointments_ns.expect(finish_appointment_request, validate=True)
    def post(self, id):
        appointment = Appointment.query.get_or_404(id)
        request = appointments_ns.payload
        services_request = request["services"]
        supplies_request = request["supplies"]
        sell = Sell(patient_id=appointment.patient_id, appointment_id=id)

        services = []
        supplies = []

        for service in services_request:
            service_row = Service.query.get_or_404(service["service_id"])
            quantity = service["quantity"]
            missing = service_row.can_produce(quantity)
            if len(missing) > 0:
                abort(
                    400,
                    {
                        "message": "Failed to finish the appointment, some services cannot be given due to a lack fo supplies",
                        "missing": missing,
                    },
                )

            # Subtracting from the inventory
            for supply in service_row.supplies:
                spent_quantity = supply.quantity * quantity
                buys = supply.supply.inventory
                index = 0
                remaining = spent_quantity
                while True:
                    buy = buys[index]
                    difference = buy.available_use_quantity - remaining
                    if difference >= 0:
                        buy.available_use_quantity = difference
                        # db.session.commit()
                        break
                    remaining = abs(difference)
                    difference = 0
                    buy.available_use_quantity = 0
                    # db.session.commit()
                    index += 1

            total = service_row.price * quantity
            vat = total * 0.16
            subtotal = total * 0.84
            new_service = SellServices(
                service_id=service_row.id,
                quantity=quantity,
                price=service_row.price,
                subtotal=subtotal,
                vat=vat,
                total=total,
            )
            services.append(new_service)

        for supply in supplies_request:
            supply_row = Supply.query.get_or_404(supply["supply_id"])
            quantity = supply["quantity"]
            if quantity > supply_row.stock_in_use_unit:
                abort(
                    400,
                    f"Failed to finish the appointment. You are trying to sell a supply with not enough stock {supply_row.stock_in_use_unit}",
                )

            # Subtracting from the inventory
            spent_quantity = quantity
            buys = supply_row.inventory
            index = 0
            remaining = spent_quantity
            while True:
                buy = buys[index]
                difference = buy.available_use_quantity - remaining
                if difference >= 0:
                    buy.available_use_quantity = difference
                    # db.session.commit()
                    break
                remaining = abs(difference)
                difference = 0
                buy.available_use_quantity = 0
                # db.session.commit()
                index += 1

            total = supply_row.price * quantity
            vat = total * 0.16
            subtotal = total * 0.84
            new_supply = SellSupplies(
                supply_id=supply_row.id,
                quantity=quantity,
                price=supply_row.price,
                subtotal=subtotal,
                vat=vat,
                total=total,
            )
            supplies.append(new_supply)

        sell.services_query = services
        sell.supplies_query = supplies

        sell.total = sum([service.total for service in services]) + sum(
            supply.total for supply in supplies
        )
        sell.subtotal = total * 0.84
        sell.vat = total * 0.16

        try:
            db.session.add(sell)
            db.session.commit()
            appointment.status = AppointmentStatus.ATENDIDA
            db.session.commit()
            return {"message": "Appointment finished successfully"}, 200
        except Exception as ex:
            db.session.rollback()
            print(f"Error while creating the sell {str(ex)}")
            abort(500, "Failed to finish the appointment. Try again later")

from .extensions import db
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import or_
from datetime import datetime
from datetime import date
from enum import Enum
import math


class UserRole(Enum):
    ADMIN = 0
    DENTIST = 1
    PATIENT = 2


class RowStatus(Enum):
    INACTIVO = 0
    ACTIVO = 1


class AppointmentStatus(Enum):
    CANCELADA = 0
    AGENDADA = 1
    ATENDIDA = 2


class SellStatus(Enum):
    CANCELADA = 0
    CREADA = 1
    PAGO_PARCIAL = 2
    PAGO_TOTAL = 3


class PaymentStatus(Enum):
    CANCELADO = 0
    PAGADO = 0


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    surname = db.Column(db.String(45), nullable=False)
    lastname = db.Column(db.String(45), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    rfc = db.Column(db.String(13), nullable=True)
    tax_regime = db.relationship("TaxRegime", lazy=True, uselist=False)
    tax_regime_id = db.Column(db.Integer, db.ForeignKey("tax_regime.id"))
    sex = db.Column(db.Boolean, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    cp = db.Column(db.String(10), nullable=False)
    latitude = db.Column(db.String(20), nullable=False)
    longitude = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    image = db.Column(db.Text, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)
    role = db.Column(db.Enum(UserRole), nullable=False)


patient_allergies = db.Table(
    "patient_allergies",
    db.Column("patient_id", db.Integer, db.ForeignKey("patient.id")),
    db.Column("allergy_id", db.Integer, db.ForeignKey("allergy.id")),
)


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship("User", lazy=True, uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    person = db.relationship("Person", lazy=True, uselist=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))
    appointments_query = db.relationship(
        "Appointment", lazy="dynamic", backref="patient"
    )
    allergies = db.relationship("Allergy", secondary=patient_allergies, lazy=True)
    sells_query = db.relationship("Sell", lazy="dynamic", backref="patient")
    payments_query = db.relationship("Payment", lazy="dynamic", backref="patient")
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)

    @hybrid_property
    def appointments(self):
        return self.appointments_query.all()

    @hybrid_property
    def sells(self):
        return self.sells_query.all()

    @hybrid_property
    def payments(self):
        return self.payments.filter(Payment.status == RowStatus.ACTIVO).all()


dentist_weekdays = db.Table(
    "dentist_weekdays",
    db.Column("dentist_id", db.Integer, db.ForeignKey("dentist.id")),
    db.Column("weekday_id", db.Integer, db.ForeignKey("weekday.id")),
)


dentist_diplomas = db.Table(
    "dentist_diplomas",
    db.Column("dentist_id", db.Integer, db.ForeignKey("dentist.id")),
    db.Column("diploma_id", db.Integer, db.ForeignKey("diploma.id")),
)


class Dentist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship("User", lazy=True, uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    person = db.relationship("Person", lazy=True, uselist=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))
    professional_license = db.Column(db.String(45), nullable=False)
    hired_at = db.Column(db.Date, nullable=False)
    position = db.Column(db.String(60), nullable=False)
    appointments_query = db.relationship(
        "Appointment", lazy="dynamic", backref="dentist"
    )
    weekdays = db.relationship("Weekday", secondary=dentist_weekdays, lazy=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    frequency = db.relationship("Frequency", lazy=True, uselist=False)
    frequency_id = db.Column(db.Integer, db.ForeignKey("frequency.id"))
    diplomas = db.relationship("Diploma", secondary=dentist_diplomas, lazy=True)
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)

    @hybrid_property
    def appointments(self):
        return self.appointments_query.all()


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    dentist_id = db.Column(db.Integer, db.ForeignKey("dentist.id"))
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"))
    sells = db.relationship("Sell", lazy=True, backref="appointment")
    status = db.Column(
        db.Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.AGENDADA
    )


class Weekday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)


class Diploma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    university = db.Column(db.String(80), nullable=False)
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)


class Allergy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)


class Frequency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)


class Supply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    cost = db.Column(db.Double, nullable=False)
    price = db.Column(db.Double, nullable=False)
    is_salable = db.Column(db.Boolean, nullable=False, default=False)
    buy_unit = db.Column(db.String(60), nullable=False)
    use_unit = db.Column(db.String(60), nullable=False)
    equivalence = db.Column(db.Double, nullable=False)
    image = db.Column(db.Text, nullable=True)
    buys_query = db.relationship("SupplyBuys", lazy="dynamic", backref="supply")
    sells_query = db.relationship("SellSupplies", lazy="dynamic", backref="supply")
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)

    @hybrid_property
    def sells(self):
        return self.sells_query.all()

    @hybrid_property
    def buy_records(self):
        return self.buys_query.order_by(SupplyBuys.buy_date.desc()).all()

    @hybrid_property
    def inventory(self):
        return (
            self.buys_query.filter(SupplyBuys.available_use_quantity > 0)
            .filter(
                or_(
                    SupplyBuys.expiration_date > date.today(),
                    SupplyBuys.expiration_date.is_(None),
                )
            )
            .order_by(SupplyBuys.expiration_date)
            .all()
        )

    @hybrid_property
    def stock(self):
        buys = self.buys_query.filter(
            or_(
                SupplyBuys.expiration_date > date.today(),
                SupplyBuys.expiration_date.is_(None),
            )
        ).all()
        stock = sum([i.available_quantity for i in buys])
        return stock

    @hybrid_property
    def stock_in_use_unit(self):
        buys = self.buys_query.filter(
            or_(
                SupplyBuys.expiration_date > date.today(),
                SupplyBuys.expiration_date.is_(None),
            )
        ).all()
        stock = sum([i.available_use_quantity for i in buys])
        return stock


class SupplyBuys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buy_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expiration_date = db.Column(db.DateTime, nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    available_use_quantity = db.Column(db.Double, nullable=False)
    unit_cost = db.Column(db.Double, nullable=False)
    supply_id = db.Column(db.Integer, db.ForeignKey("supply.id"), nullable=False)
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)

    @hybrid_property
    def available_quantity(self):
        return self.available_use_quantity / self.supply.equivalence

    @hybrid_property
    def total_cost(self):
        return self.unit_cost * self.quantity


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Double, nullable=False)
    supplies_query = db.relationship(
        "ServiceSupplies", lazy="dynamic", backref="service"
    )
    sells_query = db.relationship("SellServices", lazy="dynamic", backref="service")
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)

    @hybrid_property
    def supplies(self):
        return self.supplies_query.all()

    @hybrid_property
    def sells(self):
        return self.sells_query.all()

    @hybrid_property
    def cost(self):
        return sum([s.supply.cost * s.quantity for s in self.supplies])

    @hybrid_method
    def can_produce(self, quantity: int) -> list:
        missing = []
        for supply in self.supplies:
            quantity_needed = supply.quantity * quantity
            quantity_in_stock = supply.supply.stock_in_use_unit
            missing_quantity = quantity_needed - quantity_in_stock
            buy_missing_quantity = math.ceil(
                missing_quantity / supply.supply.equivalence
            )
            if missing_quantity > 0:
                missing.append(
                    {
                        "name": supply.supply.name,
                        "missing": missing_quantity,
                        "buy_missing": buy_missing_quantity,
                        "buy_unit": supply.supply.buy_unit,
                        "use_unit": supply.supply.use_unit,
                    }
                )
        return missing


class ServiceSupplies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
    supply_id = db.Column(db.Integer, db.ForeignKey("supply.id"), nullable=False)
    supply = db.relationship("Supply", lazy=True, uselist=False)

    @hybrid_property
    def quantityCost(self):
        return self.supply.cost / self.supply.equivalence * self.quantity


class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    key = db.Column(db.String(2), nullable=False)
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)


class PaymentWay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    key = db.Column(db.String(3), nullable=False)
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)


class TaxRegime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    key = db.Column(db.String(3), nullable=False)
    _type = db.Column(db.SmallInteger, nullable=False)
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)


class Sell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"))
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id"))
    created_at = db.Column(db.DateTime, default=db.func.now())
    paid_at = db.Column(db.DateTime, nullable=True)
    subtotal = db.Column(db.Double, nullable=False)
    vat = db.Column(db.Double, nullable=False)
    total = db.Column(db.Double, nullable=False)
    services_query = db.relationship("SellServices", lazy="dynamic", backref="Sell")
    supplies_query = db.relationship("SellSupplies", lazy="dynamic", backref="Sell")
    # payment_method_id = db.Column(db.Integer, db.ForeignKey("payment_method.id"))
    # payment_method = db.relationship("PaymentMethod", lazy=True, uselist=False)
    status = db.Column(db.Enum(SellStatus), nullable=False, default=SellStatus.CREADA)

    @hybrid_property
    def services(self):
        return self.services_query.filter(SellServices.status == RowStatus.ACTIVO).all()

    @hybrid_property
    def supplies(self):
        return self.supplies_query.filter(SellSupplies.status == RowStatus.ACTIVO).all()


class SellServices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sell_id = db.Column(db.Integer, db.ForeignKey("sell.id"))
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Double, nullable=False)
    subtotal = db.Column(db.Double, nullable=False)
    vat = db.Column(db.Double, nullable=False)
    total = db.Column(db.Double, nullable=False)
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)


class SellSupplies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sell_id = db.Column(db.Integer, db.ForeignKey("sell.id"))
    supply_id = db.Column(db.Integer, db.ForeignKey("supply.id"))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Double, nullable=False)
    subtotal = db.Column(db.Double, nullable=False)
    vat = db.Column(db.Double, nullable=False)
    total = db.Column(db.Double, nullable=False)
    status = db.Column(db.Enum(RowStatus), nullable=False, default=RowStatus.ACTIVO)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sell_id = db.Column(db.Integer, db.ForeignKey("sell.id"))
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"))
    subtotal = db.Column(db.Double, nullable=False)
    vat = db.Column(db.Double, nullable=False)
    total = db.Column(db.Double, nullable=False)
    status = db.Column(
        db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.PAGADO
    )

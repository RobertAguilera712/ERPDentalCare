from .extensions import db
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from datetime import date


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
    latitude = db.Column(db.Double, nullable=False)
    longitude = db.Column(db.Double, nullable=False)
    phone = db.Column(db.String(12), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    image = db.Column(db.Text, nullable=True)
    password = db.Column(db.String(60), nullable=False)


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
    appointments = db.relationship("Appointment", lazy="dynamic", backref="patient")
    allergy = db.relationship("Allergy", secondary=patient_allergies, lazy=True)
    sells = db.relationship("Sell", lazy=True, backref='patient')
    payments = db.relationship("Payment", lazy=True, backref='patient')


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
    appointments = db.relationship("Appointment", lazy="dynamic", backref="dentist")
    schedules = db.relationship("Schedule", lazy="dynamic", backref="dentist")
    weekdays = db.relationship("Weekday", secondary=dentist_weekdays, lazy=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    frequency = db.relationship("Frequency", lazy=True, uselist=False)
    frequency_id = db.Column(db.Integer, db.ForeignKey("frequency.id"))
    diplomas = db.relationship("Diploma", secondary=dentist_diplomas, lazy=True)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    star_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    dentist_id = db.Column(db.Integer, db.ForeignKey("dentist.id"))
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"))
    schedules = db.relationship("Schedule", lazy="dynamic", backref="appointment")
    sells = db.relationship("Sell", lazy=True, backref='appointment')


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    star_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    dentist_id = db.Column(db.Integer, db.ForeignKey("dentist.id"))
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id"))


class Weekday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)


class Diploma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)


class Allergy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)


class Frequency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    duration = db.Column(db.Integer, nullable=False)


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
    buys = db.relationship("SupplyBuys", lazy="dynamic", backref="supply")
    sells = db.relationship("SellSupplies", lazy=True, backref='supply')

    @hybrid_property
    def buy_records(self):
        return self.buys.order_by(SupplyBuys.buy_date.desc()).all()

    @hybrid_property
    def inventory(self):
        return (
            self.buys.filter(SupplyBuys.available_use_quantity > 0)
            .filter(SupplyBuys.expiration_date > date.today())
            .order_by(SupplyBuys.expiration_date)
            .all()
        )

    @hybrid_property
    def stock(self):
        buys = self.buys.filter(SupplyBuys.expiration_date > date.today()).all()
        stock = sum([i.available_quantity for i in buys])
        return stock

    @hybrid_property
    def stock_in_use_unit(self):
        buys = self.buys.filter(SupplyBuys.expiration_date > date.today()).all()
        stock = sum([i.available_use_quantity for i in buys])
        return stock


class SupplyBuys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buy_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expiration_date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    available_use_quantity = db.Column(db.Double, nullable=False)
    unit_cost = db.Column(db.Double, nullable=False)
    supply_id = db.Column(db.Integer, db.ForeignKey("supply.id"), nullable=False)

    @hybrid_property
    def available_quantity(self):
        return self.available_use_quantity / self.supply.equivalence

    @hybrid_property
    def total_cost(self):
        return self.unit_cost * self.quantity


# SERVICES, SELLS, PAYMENT, SAT, Sell details, service supplies

service_supplies = db.Table(
    "service_supplies",
    db.Column("service_id", db.Integer, db.ForeignKey("service.id")),
    db.Column("supply_id", db.Integer, db.ForeignKey("supply.id")),
)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Double, nullable=False)
    supplies = db.relationship("Supply", secondary=service_supplies, lazy=True)
    sells = db.relationship("SellServices", lazy=True, backref='service')

    @hybrid_property
    def cost(self):
        return sum([supply.cost for supply in self.supplies])


class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    key = db.Column(db.String(2), nullable=False)


class PaymentWay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    key = db.Column(db.String(3), nullable=False)


class TaxRegime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    key = db.Column(db.String(3), nullable=False)
    _type = db.Column(db.SmallInteger, nullable=False)


class Sell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"))
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id"))
    created_at = db.Column(db.DateTime, default=db.func.now())
    paid_at = db.Column(db.DateTime, nullable=True)
    subtotal = db.Column(db.Double, nullable=False)
    vat = db.Column(db.Double, nullable=False)
    total = db.Column(db.Double, nullable=False)
    services = db.relationship("SellServices", lazy=True, backref="Sell")
    supplies = db.relationship("SellSupplies", lazy=True, backref="Sell")
    payments = db.relationship("Payments", lazy=True, backref="Sell")

    @hybrid_property
    def balance(self):
        return self.total - sum([payment.total for payment in self.payments])

    @hybrid_property
    def paid(self):
        return self.balance == 0


class SellServices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sell_id = db.Column(db.Integer, db.ForeignKey("sell.id"))
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Double, nullable=False)
    subtotal = db.Column(db.Double, nullable=False)
    vat = db.Column(db.Double, nullable=False)
    total = db.Column(db.Double, nullable=False)


class SellSupplies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sell_id = db.Column(db.Integer, db.ForeignKey("sell.id"))
    supply_id = db.Column(db.Integer, db.ForeignKey("supply.id"))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Double, nullable=False)
    subtotal = db.Column(db.Double, nullable=False)
    vat = db.Column(db.Double, nullable=False)
    total = db.Column(db.Double, nullable=False)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sell_id = db.Column(db.Integer, db.ForeignKey("sell.id"))
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"))
    payment_method = db.relationship("PaymentMethod", lazy=True, uselist=False)
    payment_method_id = db.Column(db.Integer, db.ForeignKey("payment_method.id"))
    subtotal = db.Column(db.Double, nullable=False)
    vat = db.Column(db.Double, nullable=False)
    total = db.Column(db.Double, nullable=False)

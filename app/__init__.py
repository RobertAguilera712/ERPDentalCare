from flask import Flask
from .extensions import api, db, jwt, bcrypt
from .config import Config
from .patients.controller import patients_ns
from .dentists.controller import dentists_ns
from .supplies.controller import supplies_ns
from .services.controller import services_ns
from .allergies.controller import allergies_ns
from .appointments.controller import appointments_ns
from .sells.controller import sells_ns
from .get.controller import get_ns
from .login.controller import login_ns
from app.models import *
from sqlalchemy import inspect, text


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    api.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    api.add_namespace(login_ns)
    api.add_namespace(patients_ns)
    api.add_namespace(dentists_ns)
    api.add_namespace(get_ns)
    api.add_namespace(supplies_ns)
    api.add_namespace(services_ns)
    api.add_namespace(appointments_ns)
    api.add_namespace(sells_ns)
    api.add_namespace(allergies_ns)

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).first()

    with app.app_context():
        create_db()
    return app


def create_db():
    inspector = inspect(db.engine)
    if not inspector.has_table(User.__tablename__):
        # Creating the db
        db.create_all()
        # Inserting tax regimes
        tax_regimes_query = text(
            """INSERT INTO tax_regime (`id`, `name`, `key`, `_type`, `status`) VALUES (1, 'Sueldos y Salarios e Ingresos Asimilados a Salarios', '605', 1, 'ACTIVO'), (2, 'Arrendamiento', '606', 1, 'ACTIVO'), (3, 'Demás ingresos', '608', 1, 'ACTIVO'), (4, 'Ingresos por Dividendos (socios y accionistas)', '611', 1, 'ACTIVO'), (5, 'Personas Físicas con Actividades Empresariales y Profesionales', '612', 1, 'ACTIVO'), (6, 'Ingresos por intereses', '614', 1, 'ACTIVO'), (7, 'Régimen de los ingresos por obtención de premios', '615', 1, 'ACTIVO'), (8, 'Sin obligaciones fiscales', '616', 1, 'ACTIVO'), (9, 'Incorporación Fiscal', '621', 1, 'ACTIVO'), (10, 'Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras', '622', 1, 'ACTIVO'), (11, 'De los Regímenes Fiscales Preferentes y de las Empresas Multinacionales', '629', 1, 'ACTIVO'), (12, 'Enajenación de acciones en bolsa de valores', '630', 1, 'ACTIVO'), (13, 'General de Ley Personas Morales', '601', 2, 'ACTIVO'), (14, 'Personas Morales con Fines no Lucrativos', '603', 2, 'ACTIVO'), (15, 'Régimen de Enajenación o Adquisición de Bienes', '607', 2, 'ACTIVO'), (16, 'Consolidación', '609', 2, 'ACTIVO'), (17, 'Sociedades Cooperativas de Producción que optan por Diferir sus Ingresos', '220', 2, 'ACTIVO'), (18, 'Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras', '622', 2, 'ACTIVO'), (19, 'Opcional para Grupos de Sociedades', '623', 2, 'ACTIVO'), (20, 'Coordinados', '624', 2, 'ACTIVO'), (21, 'Hidrocarburos', '628', 2, 'ACTIVO');"""
        )

        db.session.execute(tax_regimes_query)
        db.session.commit()

        # Insert weekdays
        weekdays_query = text(
            """INSERT INTO `weekday` (`id`, `name`, `status`) VALUES (1, 'Lunes', 'ACTIVO'), (2, 'Martes', 'ACTIVO'), (3, 'Miércoles', 'ACTIVO'), (4, 'Jueves', 'ACTIVO'), (5, 'Viernes', 'ACTIVO'), (6, 'Sábado', 'ACTIVO'), (7, 'Domingo', 'ACTIVO'); """
        )

        db.session.execute(weekdays_query)
        db.session.commit()

        # Insert frequencies
        frequencies_query = text(
            """INSERT INTO `frequency` (`id`, `name`, `duration`, `status`) VALUES (1, 'Semanal', 7, 'ACTIVO'), (2, 'Quincenal', 14, 'ACTIVO'), (3, 'Mensual', 28, 'ACTIVO'); """
        )

        db.session.execute(frequencies_query)
        db.session.commit()

        # Insert a dentist

        # Create a new dentist and a new patient
        new_dentist = Dentist()

        # Define data for the dentist
        hashed_password = bcrypt.generate_password_hash("password").decode("utf-8")
        admin_user = User(
            email="admin@gmail.com", password=hashed_password, role=UserRole.ADMIN
        )
        db.session.add(admin_user)
        db.session.commit()

        new_dentist.user = User(
            email="dentist@gmail.com", password=hashed_password, role=UserRole.DENTIST
        )
        new_dentist.person = Person(
            name="John",
            surname="Doe",
            lastname="Smith",
            birthday="1990-01-01",
            sex=True,
            address="123 Dentist St",
            cp="12345",
            latitude="12.3456",
            longitude="78.9012",
            phone="1234567890",
        )
        new_dentist.professional_license = "D12345"
        new_dentist.hired_at = "2023-10-24"
        new_dentist.position = "Dentist"
        new_dentist.start_time = "08:00:00"
        new_dentist.end_time = "17:00:00"
        new_dentist.weekdays.extend = Weekday.query.filter(
            Weekday.id.in_([1, 2, 3, 4, 5])
        ).all()
        new_dentist.diplomas.append(
            Diploma(name="Orthodontist", university="Dental College")
        )
        new_dentist.frequency_id = 1

        db.session.add(new_dentist)
        db.session.commit()

        new_patient = Patient()

        # Define data for the patient
        new_patient.user = User(
            email="patient@gmail.com", password=hashed_password, role=UserRole.PATIENT
        )
        new_patient.person = Person(
            name="Alice",
            surname="Johnson",
            lastname="Brown",
            birthday="1995-05-15",
            sex=False,
            address="456 Patient Ln",
            cp="54321",
            latitude="34.5678",
            longitude="87.6543",
            phone="987-654-3210",
            status="ACTIVO",
        )
        new_patient.allergies.append(Allergy(name="paracetamol"))

        db.session.add(new_patient)
        db.session.commit()

        new_supply = Supply(
            name="Dental Floss",
            cost=1.50,
            price=3.99,
            is_salable=True,
            buy_unit="Pack",
            use_unit="Piece",
            equivalence=50,  # 50 pieces per pack
            image="path_to_dental_floss_image.jpg",  # Set to the image path if available
            status=RowStatus.ACTIVO,  # Make sure RowStatus is imported and defined
        )

        # Add the new object to the session and commit the session
        db.session.add(new_supply)
        db.session.commit()

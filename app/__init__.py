from flask import Flask 
from flask_cors import CORS
from .extensions import api, db
from .config import Config
from .patients.controller import patients_ns
from .dentists.controller import dentists_ns
from .supplies.controller import supplies_ns
from .services.controller import services_ns
from .schedules.controller import schedule_ns
from .appointments.controller import appointments_ns
from .get.controller import get_ns
from app.models import *
from sqlalchemy import inspect, text


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    api.init_app(app)
    db.init_app(app)
    api.add_namespace(patients_ns)
    api.add_namespace(dentists_ns)
    api.add_namespace(get_ns)
    api.add_namespace(supplies_ns)
    api.add_namespace(services_ns)
    api.add_namespace(schedule_ns)
    api.add_namespace(appointments_ns)

    CORS(app)

    with app.app_context():
        create_db()
    return app


def create_db():
    inspector = inspect(db.engine)
    if not inspector.has_table(User.__tablename__):
        # Creating the db
        db.create_all()
        # Inserting tax regimes
        tax_regimes_query = text("""INSERT INTO tax_regime (`id`, `name`, `key`, `_type`, `status`) VALUES (1, 'Sueldos y Salarios e Ingresos Asimilados a Salarios', '605', 1, 'ACTIVO'), (2, 'Arrendamiento', '606', 1, 'ACTIVO'), (3, 'Demás ingresos', '608', 1, 'ACTIVO'), (4, 'Ingresos por Dividendos (socios y accionistas)', '611', 1, 'ACTIVO'), (5, 'Personas Físicas con Actividades Empresariales y Profesionales', '612', 1, 'ACTIVO'), (6, 'Ingresos por intereses', '614', 1, 'ACTIVO'), (7, 'Régimen de los ingresos por obtención de premios', '615', 1, 'ACTIVO'), (8, 'Sin obligaciones fiscales', '616', 1, 'ACTIVO'), (9, 'Incorporación Fiscal', '621', 1, 'ACTIVO'), (10, 'Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras', '622', 1, 'ACTIVO'), (11, 'De los Regímenes Fiscales Preferentes y de las Empresas Multinacionales', '629', 1, 'ACTIVO'), (12, 'Enajenación de acciones en bolsa de valores', '630', 1, 'ACTIVO'), (13, 'General de Ley Personas Morales', '601', 2, 'ACTIVO'), (14, 'Personas Morales con Fines no Lucrativos', '603', 2, 'ACTIVO'), (15, 'Régimen de Enajenación o Adquisición de Bienes', '607', 2, 'ACTIVO'), (16, 'Consolidación', '609', 2, 'ACTIVO'), (17, 'Sociedades Cooperativas de Producción que optan por Diferir sus Ingresos', '220', 2, 'ACTIVO'), (18, 'Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras', '622', 2, 'ACTIVO'), (19, 'Opcional para Grupos de Sociedades', '623', 2, 'ACTIVO'), (20, 'Coordinados', '624', 2, 'ACTIVO'), (21, 'Hidrocarburos', '628', 2, 'ACTIVO');""")
        
        db.session.execute(tax_regimes_query)
        db.session.commit()

        # Insert weekdays
        weekdays_query = text("""INSERT INTO `weekday` (`id`, `name`, `status`) VALUES (1, 'Lunes', 'ACTIVO'), (2, 'Martes', 'ACTIVO'), (3, 'Miércoles', 'ACTIVO'), (4, 'Jueves', 'ACTIVO'), (5, 'Viernes', 'ACTIVO'), (6, 'Sábado', 'ACTIVO'), (7, 'Domingo', 'ACTIVO'); """)

        db.session.execute(weekdays_query)
        db.session.commit()

        # Insert frequencies

        frequencies_query = text("""INSERT INTO `frequency` (`id`, `name`, `duration`, `status`) VALUES (1, 'Semanal', 7, 'ACTIVO'), (2, 'Quincenal', 14, 'ACTIVO'), (3, 'Mensual', 28, 'ACTIVO'); """)

        db.session.execute(frequencies_query)
        db.session.commit()

        
        
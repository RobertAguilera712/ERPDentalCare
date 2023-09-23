from flask import Flask 

from .extensions import api, db
from .config import Config
from .patients.controller import patients_ns
from .dentists.controller import dentists_ns
from .supplies.controller import supplies_ns
from .services.controller import services_ns
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

    with app.app_context():
        create_db()
    return app


def create_db():
    inspector = inspect(db.engine)
    if not inspector.has_table(User.__tablename__):
        # Creating the db
        db.create_all()
        # Inserting tax regimes
        tax_regimes_query = text("""INSERT INTO tax_regime (`id`, `name`, `key`, `_type`, `status`) VALUES (1, 'Sueldos y Salarios e Ingresos Asimilados a Salarios', '605', 1, 1), (2, 'Arrendamiento', '606', 1, 1), (3, 'Demás ingresos', '608', 1, 1), (4, 'Ingresos por Dividendos (socios y accionistas)', '611', 1, 1), (5, 'Personas Físicas con Actividades Empresariales y Profesionales', '612', 1, 1), (6, 'Ingresos por intereses', '614', 1, 1), (7, 'Régimen de los ingresos por obtención de premios', '615', 1, 1), (8, 'Sin obligaciones fiscales', '616', 1, 1), (9, 'Incorporación Fiscal', '621', 1, 1), (10, 'Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras', '622', 1, 1), (11, 'De los Regímenes Fiscales Preferentes y de las Empresas Multinacionales', '629', 1, 1), (12, 'Enajenación de acciones en bolsa de valores', '630', 1, 1), (13, 'General de Ley Personas Morales', '601', 2, 1), (14, 'Personas Morales con Fines no Lucrativos', '603', 2, 1), (15, 'Régimen de Enajenación o Adquisición de Bienes', '607', 2, 1), (16, 'Consolidación', '609', 2, 1), (17, 'Sociedades Cooperativas de Producción que optan por Diferir sus Ingresos', '220', 2, 1), (18, 'Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras', '622', 2, 1), (19, 'Opcional para Grupos de Sociedades', '623', 2, 1), (20, 'Coordinados', '624', 2, 1), (21, 'Hidrocarburos', '628', 2, 1);""")
        
        db.session.execute(tax_regimes_query)
        db.session.commit()

        # Insert weekdays
        weekdays_query = text("""INSERT INTO `weekday` (`id`, `name`, `status`) VALUES (1, 'Lunes', 1), (2, 'Martes', 1), (3, 'Miércoles', 1), (4, 'Jueves', 1), (5, 'Viernes', 1), (6, 'Sábado', 1), (7, 'Domingo', 1); """)

        db.session.execute(weekdays_query)
        db.session.commit()

        # Insert frequencies

        frequencies_query = text("""INSERT INTO `frequency` (`id`, `name`, `duration`, `status`) VALUES (1, 'Semanal', 7, 1), (2, 'Quincenal', 14, 1), (3, 'Mensual', 28, 1); """)

        db.session.execute(frequencies_query)
        db.session.commit()
        
        
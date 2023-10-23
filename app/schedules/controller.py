from flask_restx import Resource, Namespace
from app.models import Schedule, Dentist, Weekday
from app.extensions import db
from .responses import schedule_response
from .requests import create_schedule_request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU



schedule_ns = Namespace("api")


@schedule_ns.route("/schedules")
class SchedulesAPI(Resource):

    @schedule_ns.expect(create_schedule_request)
    @schedule_ns.marshal_with(schedule_response)
    def post(self):
        date_format = "%Y-%m-%d"

        request = schedule_ns.payload

        start_date = datetime.strptime(request["start_date"], date_format) 
        end_date = datetime.strptime(request["end_date"], date_format) 

        dentist_id = request["dentist_id"]

        dentist = Dentist.query.get_or_404(dentist_id)
        current_date = start_date

        weekdays = {
            1: MO,
            2: TU,
            3: WE,
            4: TH,
            5: FR,
            6: SA,
            7: SU,
        }

        frequencies = {
            1: 1,
            2: 3,
            3: 4
        }

        schedules = []

        dentist.weekdays.sort(key=lambda wd: wd.id)
        frequency = frequencies[dentist.frequency_id]

        while current_date < end_date:
            for weekday in dentist.weekdays:
                next_day = weekdays[weekday.id]
                current_date = (current_date + relativedelta(weekday=next_day(frequency))) 

                current_time = dentist.start_time
                end_time = dentist.end_time

                while  current_time < end_time:
                    schedule_start = datetime.combine(current_date, current_time)
                    schedule_end = schedule_start + timedelta(minutes=30)
                    schedule = Schedule(start_date = schedule_start, end_date = schedule_end, dentist_id = dentist_id )
                    schedules.append(schedule)
                    current_time = schedule_end.time()

        db.session.add_all(schedules)
        db.session.commit()
                

        return schedules, 201



    

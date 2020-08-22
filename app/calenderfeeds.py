from datetime import date, timedelta
from io import BytesIO

from dateutil import parser

from flask import Blueprint, make_response
from icalendar import Calendar, Event, vDatetime

from app import eventor_utils
from definitions import config

calendarfeeds_app = Blueprint('calendarfeeds', __name__)


def add_activities(root, calendar: Calendar):
    for activity in root:
        try:
            attributes = activity.attrib
            cal_event = Event()

            cal_event['summary'] = activity.find('Name').text + ' [KLUBBAKTIVITET]'

            starttime = parser.parse(attributes['startTime'])
            cal_event['dtstart'] = vDatetime(starttime).to_ical()

            endtime = starttime + timedelta(hours=2)
            cal_event['dtend'] = vDatetime(endtime).to_ical()

            cal_event['url'] = attributes['url']

            cal_event['uid'] = 'Activity_' + attributes['id'] + '@eventor.orientering.se'

            calendar.add_component(cal_event)
        except RuntimeError as err:
            print(err)
            continue


def add_events(root, calendar: Calendar):
    for event in root:
        try:
            cal_event = Event()

            name = event.find('Name').text

            org_id = event.find('Organiser').find('OrganisationId').text
            org_name = eventor_utils.org_name(org_id)
            cal_event['summary'] = '{}, {}'.format(name, org_name)
            print(cal_event['summary'])

            startdate_str = event.find('StartDate').find('Date').text
            starttime_str = event.find('StartDate').find('Clock').text
            startdatetime = parser.parse(startdate_str + ' ' + starttime_str)

            enddate_str = event.find('StartDate').find('Date').text
            endtime_str = event.find('StartDate').find('Clock').text
            enddatetime = parser.parse(enddate_str + ' ' + endtime_str)

            if startdatetime == enddatetime:
                enddatetime = startdatetime + timedelta(hours=3)

            cal_event['dtstart'] = vDatetime(startdatetime).to_ical()

            cal_event['dtend'] = vDatetime(enddatetime).to_ical()

            cal_event['url'] = 'https://eventor.orientering.se/Events/Show/' + event.find('EventId').text

            cal_event['uid'] = 'Event_' + event.find('EventId').text + '@eventor.orientering.se'

            calendar.add_component(cal_event)
        except RuntimeError as err:
            print(err)
            continue


@calendarfeeds_app.route('/calendarfeed/<int:days_in_advance>', methods=['GET'])
def calendarfeed(days_in_advance: int):
    calendar = Calendar()

    start = date.today()
    end = start + timedelta(days=days_in_advance)
    activities_root = eventor_utils.club_activities(start, end)
    add_activities(activities_root, calendar)
    districs_events_root = eventor_utils.events(start, end, [1, 2, 3, 4, 6], [config['EventorApi']['district_id']])
    add_events(districs_events_root, calendar)

    club_events_root = eventor_utils.events(start, end, [5], [config['EventorApi']['organisation_id']])
    add_events(club_events_root, calendar)

    io = BytesIO()
    io.write(calendar.to_ical())
    try:
        response = make_response(io.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=calendar.ics"
        return response
    except IOError:
        raise Exception(config['Errors']['io_error'], 'eventor')

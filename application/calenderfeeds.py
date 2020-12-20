from datetime import date, timedelta, time
from io import BytesIO

from dateutil import parser
import pytz
from flask import Blueprint, make_response
from icalendar import Calendar, Event, vDatetime

from application import eventor_utils
from definitions import config

calendarfeeds_app = Blueprint('calendarfeeds', __name__)

timezone = pytz.timezone(config['Time']['timezone'])


def add_activities(root, calendar: Calendar):
    for activity in root:
        try:
            attributes = activity.attrib
            cal_event = Event()

            cal_event['summary'] = '{} [{} anmälda]'.format(activity.find('Name').text, attributes['registrationCount'])

            starttime = parser.parse(attributes['startTime'])
            starttime = starttime.astimezone(timezone)
            cal_event['dtstart'] = vDatetime(starttime).to_ical()

            if starttime.time() == time(0, 0, 0):
                endtime = starttime + timedelta(days=1)
            else:
                endtime = starttime + timedelta(hours=3)
            cal_event['dtend'] = vDatetime(endtime).to_ical()

            cal_event['categories'] = ','.join(['Eventor', 'Klubbaktivitet'])

            cal_event['description'] = 'Denna aktivitet är importerad från Eventor, för info se: {}'.format(
                attributes['url'])

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

            startdate_str = event.find('StartDate').find('Date').text
            starttime_str = event.find('StartDate').find('Clock').text
            startdatetime = parser.parse(startdate_str + ' ' + starttime_str)
            startdatetime = timezone.localize(startdatetime)

            enddate_str = event.find('StartDate').find('Date').text
            endtime_str = event.find('StartDate').find('Clock').text
            enddatetime = parser.parse(enddate_str + ' ' + endtime_str)
            enddatetime = timezone.localize(enddatetime)

            if startdatetime == enddatetime:
                if startdatetime.time() == time(0, 0, 0, tzinfo=timezone):
                    enddatetime = startdatetime + timedelta(days=1)
                else:
                    enddatetime = startdatetime + timedelta(hours=3)

            cal_event['dtstart'] = vDatetime(startdatetime).to_ical()

            cal_event['dtend'] = vDatetime(enddatetime).to_ical()

            classification = config['EventClassification'][str(event.find('EventClassificationId').text)]
            cal_event['categories'] = ','.join(['Eventor', classification])

            url = 'https://eventor.orientering.se/Events/Show/' + event.find('EventId').text
            cal_event['url'] = url

            cal_event['description'] = 'Denna aktivitet är importerad från Eventor, för info se: {}'.format(url)

            cal_event['uid'] = 'Event_' + event.find('EventId').text + '@eventor.orientering.se'

            calendar.add_component(cal_event)
        except RuntimeError as err:
            print(err)
            continue


@calendarfeeds_app.route('/calendarfeed/<int:days_in_advance>', methods=['GET'])
def calendarfeed(days_in_advance: int):
    calendar = Calendar()
    calendar['method'] = 'REQUEST'
    calendar['prodid'] = '-//Svenska Orienteringsförbundet//GMOK'
    calendar['version'] = '2.0'

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
        response.headers["Content-Disposition"] = "attachment; filename=Events.ics"
        return response
    except IOError:
        raise Exception(config['Errors']['io_error'], 'eventor')

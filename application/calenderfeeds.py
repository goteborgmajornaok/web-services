import json
import os
from datetime import date, timedelta, time

import requests
from dateutil import parser
import pytz
from flask import Blueprint, make_response, request, jsonify
from icalendar import Calendar, Event, vDatetime
from icalendar.prop import vCategory, vText

from application import eventor_utils
from application.request_handler import api_request
from common import check_api_key
from definitions import config, ROOT_DIR

calendarfeeds_app = Blueprint('calendarfeeds', __name__)

timezone = pytz.timezone(config['Time']['timezone'])


def add_activities(root, calendar: Calendar):
    for activity in root:
        try:
            attributes = activity.attrib
            cal_event = Event()

            cal_event['summary'] = '{} [{} anmälda]'.format(activity.find('Name').text, attributes['registrationCount'])

            if 'startTime' not in attributes:
                continue

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


def is_cancelled(event):
    if 'EventStatusId' in [t.tag for t in event.iter()]:
        return event.find('EventStatusId').text == config['Calendar']['cancelled_status_id']
    return False


def add_events(root, calendar: Calendar):
    for event in root:
        try:
            cal_event = Event()

            name = event.find('Name').text
            if is_cancelled(event):
                name = '[INSTÄLLD] ' + name

            org_id = event.find('Organiser').find('OrganisationId').text
            org_name = eventor_utils.org_name(org_id)
            cal_event['summary'] = '{}, {}'.format(name, org_name)

            startdate_str = event.find('StartDate').find('Date').text
            starttime_str = event.find('StartDate').find('Clock').text
            startdatetime = parser.parse(startdate_str + ' ' + starttime_str)
            startdatetime = timezone.localize(startdatetime)

            enddate_str = event.find('FinishDate').find('Date').text
            endtime_str = event.find('FinishDate').find('Clock').text
            enddatetime = parser.parse(enddate_str + ' ' + endtime_str)
            enddatetime = timezone.localize(enddatetime)

            if startdatetime == enddatetime:
                if startdatetime.time() == time(0, 0, 0, tzinfo=timezone):
                    enddatetime = startdatetime + timedelta(days=1)
                else:
                    enddatetime = startdatetime + timedelta(hours=3)

            elif startdatetime.date() != enddatetime.date() and enddatetime.time() == time(0, 0, 0, tzinfo=timezone):
                enddatetime += timedelta(days=1)

            cal_event.add('dtstart', startdatetime)

            cal_event.add('dtend', enddatetime)

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


def add_idrottonline_feeds(calendar: Calendar):
    try:
        with open('idrottonline_feeds.json', "r") as json_file:
            data = json.load(json_file)

        for feed in data:
            feed_calendar = Calendar.from_ical(requests.get(feed['url']).text)
            calendar_name = vText.from_ical(feed_calendar['X-WR-CALNAME'])
            for component in feed_calendar.subcomponents:
                if 'categories' in component:
                    old_categories = [vCategory.from_ical(c)[0] for c in component['categories'].cats if
                                      vCategory.from_ical(c)[0] != '"']
                    new_categories = feed['categories'] + old_categories
                    component['categories'] = ','.join(new_categories)
                else:
                    component['categories'] = ','.join(feed_calendar['categories'])

                idrottonline_id = vText.from_ical(component['UID']).split('Activity')[1].split('@')[0]
                url = config['IdrottOnline'][
                          'activity_base_url'] + '/' + calendar_name + '?calendarEventId=' + idrottonline_id
                component['url'] = url
                if 'description' in component:
                    description = vText.from_ical(component['description'])
                    description = description.replace('[', '<').replace(']', '>')
                else:
                    description = ''
                component[
                    'description'] = description + 'Denna aktivitet är importerad från IdrottOnline, se: {}'.format(
                    url)
                calendar.add_component(component)
    except IOError:
        return


def generate_calendarfeed(days_in_advance: int):
    calendar = Calendar()
    calendar['method'] = 'REQUEST'
    calendar['prodid'] = '-//Svenska Orienteringsförbundet//GMOK'
    calendar['version'] = '2.0'

    start = date.today()
    end = start + timedelta(days=days_in_advance)

    # Fetch club activities
    activities_root = eventor_utils.club_activities(start, end)
    add_activities(activities_root, calendar)

    # Fetch district events

    districs_events_root = eventor_utils.events(start, end, config['Calendar']['district_event_class_ids'].split(','),
                                                [config['EventorApi']['district_id']])
    add_events(districs_events_root, calendar)

    # Fetch club events
    club_events_root = eventor_utils.events(start, end, config['Calendar']['club_event_class_ids'].split(','),
                                            [config['EventorApi']['organisation_id']])
    add_events(club_events_root, calendar)

    # Add feeds from other webcals
    add_idrottonline_feeds(calendar)

    f = open(config.get('Calendar', 'filename'), 'wb')
    f.write(calendar.to_ical())
    f.close()

    return jsonify({'message': 'Calendarfeed successfully generated for next {} days'.format(days_in_advance)})


def overwrite_changed(calendar):
    target_feed = Calendar.from_ical(api_request('GET', config['Calendar']['target_feed'], '', ''))

    target_dict = dict()
    for component in target_feed.subcomponents:
        if 'UID' in component and 'DESCRIPTION' in component:
            target_dict[component['UID']] = component['DESCRIPTION']

    for component in calendar.subcomponents:
        if 'UID' in component and component['UID'] in target_dict:
            component['DESCRIPTION'] = target_dict[component['UID']]


def fetch_calendarfeed():
    if not os.path.exists(config['Calendar']['filename']):
        return jsonify({"message": "Calendarfeed not generated"}), 503

    latest_ics = ROOT_DIR + '/' + config['Calendar']['filename']
    with open(latest_ics, 'rb') as f:
        calendar = Calendar.from_ical(f.read())

    try:
        response = make_response(calendar.to_ical())
        response.headers["Content-Disposition"] = "attachment; filename=Events.ics"
        return response
    except IOError:
        raise Exception(config['Errors']['io_error'], 'eventor')


@calendarfeeds_app.route('/calendarfeed', methods=['GET'])
@calendarfeeds_app.route('/calendarfeed/<int:days_in_advance>', methods=['POST'])
def calendarfeed(days_in_advance: int = None):
    if request.method == 'POST':
        if not check_api_key(request.headers):
            return jsonify({"message": "ERROR: Unauthorized"}), 401
        if isinstance(days_in_advance, int):
            return generate_calendarfeed(days_in_advance)
        else:
            return jsonify('Specify how many days to generate feed for'), 400
    elif request.method == 'GET':
        return fetch_calendarfeed()

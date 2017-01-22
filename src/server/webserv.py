from flask import Flask, request, send_from_directory, make_response
from json import dumps as jsonify
from datetime import datetime as dt
from datetime import timedelta
from server.database import session as db
from server.database import init_db
from server.models import Event

import sqlalchemy as sa

app = Flask(__name__)

counters = ['sm','lo','la']

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static',
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/")
def index():
    return send_from_directory('static','index.html')

@app.route("/stats")
def stats():
    return send_from_directory('static','stats.html')

@app.route("/count/new/<event>")
def inc_count(event):
    if event.lower() not in counters:
        return "Invalid counter"
    e = Event(event_type=event.lower())
    db.add(e)
    db.commit()
    return str(Event.query.count())

@app.route("/count", methods=['POST'])
def view_advanced():
    params = request.get_json()
    if params is None:
        return "No parameters"

    if 'event_type' in params:
        if params['event_type'] in counters:
            event_type = params['event_type']
        elif params['event_type'] == 'all':
            event_type = params['event_type']
        else:
            return "Invalid event_type"
    else:
        event_type = None

    if 'resolution' in params:
        if params['resolution'] in ['day','month','year']:
            resolution = params['resolution']
        else:
            return "Invalid resolution"
    else:
        resolution = None

    events = db.query(sa.extract('year',Event.timestamp),
                      sa.extract('month',Event.timestamp),
                      sa.extract('day',Event.timestamp),
                      Event.event_type, sa.func.count(Event.id))

    if event_type == 'all':
        events = events.group_by(Event.event_type)
    elif event_type is not None:
        events = events.filter_by(event_type=event_type.lower())

    if resolution is not None:
        events = events.group_by(sa.extract(resolution,Event.timestamp))

    data = {'sm':[], 'lo':[], 'la':[]}
    for event in events.all():
        dict_event = {'count':event[4]}
        if resolution == 'day':
            dict_event['date'] = '%4d-%02d-%02d' % event[0:3]
        elif resolution == 'month':
            dict_event['date'] = '%4d-%02d' % event[0:2]
        elif resolution == 'year':
            dict_event['date'] = '%4d' % event[0]
        else:
            dict_event['date'] = 'all'

        data[event[3]].append(dict_event)

    data['sm'].sort(key=lambda x: x['date'])
    data['lo'].sort(key=lambda x: x['date'])
    data['la'].sort(key=lambda x: x['date'])

    return make_response(jsonify(data),{'Content-Type':'application/json'})

@app.route("/count/view/")
def view_total():
    return str(Event.query.count())

@app.route("/count/view/<event>/")
def view_event_count(event):
    if event.lower() not in counters:
        return "Invalid counter"
    return str(Event.query.filter_by(event_type=event.lower()).count())

@app.route("/count/view/<event>/today")
def view_today(event):
    if event.lower() not in counters:
        return "Invalid counter"
    today = dt.now() - timedelta(hours=24)
    return str(Event.query.filter(Event.event_type == event.lower(),Event.timestamp > today).count())

@app.route("/count/view/<event>/week")
def view_weekly(event):
    if event.lower() not in counters:
        return "Invalid counter"
    weekly = dt.now() - timedelta(days=7)
    return str(Event.query.filter(Event.event_type == event.lower(),Event.timestamp > weekly).count())

@app.route("/count/view/<event>/month")
def view_monthly(event):
    if event.lower() not in counters:
        return "Invalid counter"
    monthly = dt.now() - timedelta(days=30)
    return str(Event.query.filter(Event.event_type == event.lower(),Event.timestamp > monthly).count())

@app.route("/count/view/<event>/year")
def view_yearly(event):
    if event.lower() not in counters:
        return "Invalid counter"
    yearly = dt.now() - timedelta(days=365)
    return str(Event.query.filter(Event.event_type == event.lower(),Event.timestamp > yearly).count())

@app.before_first_request
def flask_init_db():
    init_db()

@app.teardown_request
def session_clear(exception=None):
    db.remove()
    if exception and db.is_active:
        db.rollback()

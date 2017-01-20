from flask import Flask, request, send_from_directory, redirect
from sqlalchemy import desc
from json import dumps as jsonify
from datetime import datetime as dt
from datetime import timedelta
from server.database import session as db
from server.database import init_db
from server.models import Event

app = Flask(__name__)

counters = ['sm','lo','la']

@app.route("/")
def index():
    return send_from_directory('static','index.html')

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
    return "Advanced query"

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

@app.route("/count/view/<event>/weekly")
def view_weekly(event):
    if event.lower() not in counters:
        return "Invalid counter"
    weekly = dt.now() - timedelta(days=7)
    return str(Event.query.filter(Event.event_type == event.lower(),Event.timestamp > weekly).count())

@app.route("/count/view/<event>/monthly")
def view_monthly(event):
    if event.lower() not in counters:
        return "Invalid counter"
    monthly = dt.now() - timedelta(days=30)
    return str(Event.query.filter(Event.event_type == event.lower(),Event.timestamp > monthly).count())

@app.route("/count/view/<event>/yearly")
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

from flask import Flask
from common_services import EventsService

app = Flask(__name__)

events_service = EventsService(logger=app.logger)


@app.route("/hello")
def hello():
    events_service.Send()
    return events_service.GetTimestamp(), 200

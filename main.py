#!/usr/bin/env python3
"""
myplace interface for the plugin https://www.npmjs.com/package/homebridge-web-thermostat-fan
"""

__author__ = "Jase Smith"
__version__ = "0.1.0"
__license__ = "MIT"

import os
import json
import requests
import time

from flask import Flask, jsonify
from flask_cors import CORS

with open("config.json") as json_data_file:
    cfgdata = json.load(json_data_file)

myPlaceUrl = "http://" + cfgdata['ac_address'] + ":" + str(cfgdata['ac_port'])
myPlaceData = []
myPlaceDataExpiry = time.time()

def updateMyPlaceData():
   if myPlaceDataExpiry < time.time():
      myPlaceData = (requests.get(url = (myPlaceUrl + "/getSystemData").text)).json()['aircons']['ac1']
      myPlaceDataExpiry = time.time() + 1


def create_app(config=None):
   app = Flask(__name__)

   # See http://flask.pocoo.org/docs/latest/config
   app.config.update(dict(DEBUG=True))
   app.config.update(config or {})
   # Setup cors headers to allow all domains
   # https://flask-cors.readthedocs.io/en/latest/
   CORS(app)

   # Definition of the routes. Put them into their own file. See also
   # Flask Blueprints: http://flask.pocoo.org/docs/latest/blueprints
   @app.route("/")
   def hello_world():
      return "Hello World"

   @app.route("/foo/<someId>")
   def foo_url_arg(someId):
      return jsonify({"echo": someId})

   @app.route("/zone/<ACZone>/status")
   def ACZoneStatus(ACZone):
      updateMyPlaceData()
      target = int(myPlaceData['zones']['z0' + ACZone ]['setTemp'])
      current = myPlaceData['zones']['z0'+ ACZone ]['setTemp']
      match myPlaceData['info']['fan']:
         case "auto":
            fan = 5
         case "high":
            fan = 4
         case "medium":
            fan = 3
         case "low":
            fan = 2
         case _:
            fan = 0
      if myPlaceData['info']['state'] == 'on' and myPlaceData['zones']['z0'+ ACZone ]['state'] == "open":
         match myPlaceData['info']['mode']:
            case "heat":
               state = 1
            case "cool":
               state = 2
            case "vent":
               state = 3
            case _:
               state = 3
      else:
         state = 0
      results = {
      "targetHeatingCoolingState": state,
      "targetTemperature": target,
      "currentHeatingCoolingState": state,
      "currentTemperature": current,
      "fanSpeed": fan
      }
      return results

   @app.route("/zone/<ACZone>/targetHeatingCoolingState/<ACValue>")
   def ACZoneStatus(ACZone,ACValue):
      urlString = myPlaceUrl + '/setAircon?json='
      if myPlaceData['info']['state'] == 'off' and ACValue > 0:
         match ACValue:
            case 3:
               urlString += '{"ac1":{"info":{"state":"on","mode":"vent"},"zones":{"z' + ACZone + '":{"state":"open"}}}'
            case 2:
               urlString += '{"ac1":{"info":{"state":"on","mode":"cool"},"zones":{"z' + ACZone + '":{"state":"open"}}}'
            case 1:
               urlString += '{"ac1":{"info":{"state":"on","mode":"heat"},"zones":{"z' + ACZone + '":{"state":"open"}}}'
         requests.get(url = urlString)
      elif ACValue == 0:
         urlString += '{"ac1":{"zones":{"z' + ACZone + '":{"state":"closed"}}}'
         requests.get(url = urlString)
      return "ok"

   @app.route("/zone/<ACZone>/targetTemperature/<ACValue>")
   def ACZoneStatus(ACZone,ACValue):
      urlString = myPlaceUrl + '/setAircon?json={"ac1":{"zones":{"z' + ACZone + '":{"setTemp":' + ACValue + '}}}'
      requests.get(url = urlString)
      return "ok"      

   @app.route("/fresh/status")
   def ACFreshStatus():
      if myPlaceData['info']['freshAirStatus'] == "on":
         return "1"
      else:
         return "0"

   @app.route("/fresh/set/<ACValue>")
   def AZFreshSet(ACValue):
      if ACValue > 0:
         urlString = myPlaceUrl + 'setAircon?json={"ac1":{"info":{"freshAirStatus":"on"}}}'
      else:
         urlString = myPlaceUrl + 'setAircon?json={"ac1":{"info":{"freshAirStatus":"off"}}}'
      requests.get(url = urlString)
      return "ok"

   @app.route("/system/status")
   def ACFreshStatus():
      if myPlaceData['info']['state'] == "on":
         return "1"
      else:
         return "0"

   @app.route("/system/set/<ACValue>")
   def AZFreshSet(ACValue):
      if ACValue > 0:
         urlString = myPlaceUrl + 'setAircon?json={"ac1":{"info":{"state":"on"}}}'
      else:
         urlString = myPlaceUrl + 'setAircon?json={"ac1":{"info":{"state":"off"}}}'
      requests.get(url = urlString)
      return "ok"

   return app

if __name__ == "__main__":
   print(json.loads((requests.get(myPlaceUrl + "/getSystemData").text)))
   port = int(os.environ.get("PORT", 8000))
   app = create_app()
   app.run(host="0.0.0.0", port=port)

#!/usr/bin/env python3
"""
myplace translation for the plugin https://github.com/phenotypic/homebridge-web-thermostat
"""

__author__ = "Jase Smith"
__version__ = "0.1.2"
__license__ = "MIT"

import os
import json
import requests
import time

from flask import Flask, jsonify, request
from flask_cors import CORS

with open("config.json") as json_data_file:
    cfgdata = json.load(json_data_file)

myPlaceUrl = "http://" + cfgdata['ac_address'] + ":" + str(cfgdata['ac_port'])
myPlaceData = []
myPlaceDataExpiry = 0.0

def updateMyPlaceData():
   global myPlaceDataExpiry
   global myPlaceData
   if myPlaceDataExpiry < time.time():
      myPlaceData = (requests.get(url = myPlaceUrl + "/getSystemData")).json()['aircons']['ac1']
      myPlaceDataExpiry = time.time() + 1


def create_app(config=None):
   app = Flask(__name__)

   # See http://flask.pocoo.org/docs/latest/config
   #app.config.update(dict(DEBUG=True))
   app.config.update(config or {})
   # Setup cors headers to allow all domains
   # https://flask-cors.readthedocs.io/en/latest/
   CORS(app)

   # Definition of the routes. Put them into their own file. See also
   # Flask Blueprints: http://flask.pocoo.org/docs/latest/blueprints
   @app.route("/")
   def hello_world():
      return "Hello World"

   @app.route("/zone/<ACZone>/status")
   def ACZoneStatus(ACZone):
      updateMyPlaceData()
      target = int(myPlaceData['zones']['z0' + ACZone ]['setTemp'])
      current = myPlaceData['zones']['z0'+ ACZone ]['measuredTemp']
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
      print(results)
      return json.dumps(results)

   @app.route("/zone/<ACZone>/targetHeatingCoolingState")
   def ACZoneSetState(ACZone):
      ACValue = request.args.get('value', default = 0, type = int)
      urlString = myPlaceUrl + '/setAircon?json='
      match ACValue:
         case 3:
            urlString += '{"ac1":{"info":{"state":"on","mode":"vent","freshAirStatus":"on"},"zones":{"z0' + ACZone + '":{"state":"open"}}}}'
         case 2:
            urlString += '{"ac1":{"info":{"state":"on","mode":"cool","freshAirStatus":"off"},"zones":{"z0' + ACZone + '":{"state":"open"}}}}'
         case 1:
            urlString += '{"ac1":{"info":{"state":"on","mode":"heat","freshAirStatus":"off"},"zones":{"z0' + ACZone + '":{"state":"open"}}}}'
         case _:
            urlString += '{"ac1":{"zones":{"z0' + ACZone + '":{"state":"close"}}}}'
      requests.get(url = urlString)
      print(urlString)
      return "ok"

   @app.route("/zone/<ACZone>/targetTemperature")
   def ACZoneSetTemp(ACZone):
      ACValue = request.args.get('value', default = 24.0, type = float)
      urlString = myPlaceUrl + '/setAircon?json={"ac1":{"zones":{"z0' + ACZone + '":{"setTemp":' + str(ACValue) + '}}}}'
      requests.get(url = urlString)
      print(urlString)
      return "ok"      

   @app.route("/fresh/status")
   def ACFreshStatus():
      if myPlaceData['info']['freshAirStatus'] == "on":
         return "1"
      else:
         return "0"

   @app.route("/fresh/set/<ACValue>")
   def ACFreshSet(ACValue):
      if ACValue > 0:
         urlString = myPlaceUrl + 'setAircon?json={"ac1":{"info":{"freshAirStatus":"on"}}}'
      else:
         urlString = myPlaceUrl + 'setAircon?json={"ac1":{"info":{"freshAirStatus":"off"}}}'
      requests.get(url = urlString)
      return "ok"

   @app.route("/system/status")
   def ACSystemStatus():
      if myPlaceData['info']['state'] == "on":
         return "1"
      else:
         return "0"

   @app.route("/system/set/<ACValue>")
   def ACSystemSet(ACValue):
      if ACValue > 0:
         urlString = myPlaceUrl + 'setAircon?json={"ac1":{"info":{"state":"on"}}}'
      else:
         urlString = myPlaceUrl + 'setAircon?json={"ac1":{"info":{"state":"off"}}}'
      requests.get(url = urlString)
      return "ok"

   return app

if __name__ == "__main__":
   port = int(os.environ.get("PORT", 8000))
   app = create_app()
   app.run(host="0.0.0.0", port=port)

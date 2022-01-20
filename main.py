#!/usr/bin/env python3
"""
Documentation
"""

__author__ = "Jase Smith"
__version__ = "0.1.0"
__license__ = "MIT"

import os
import json
import requests

from flask import Flask, jsonify
from flask_cors import CORS

with open("config.json") as json_data_file:
    cfgdata = json.load(json_data_file)

myPlaceUrl = "http://" + cfgdata['ac_address'] + ":" + str(cfgdata['ac_port'])

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

   return app

if __name__ == "__main__":
   print(json.loads((requests.get(myPlaceUrl + "/getSystemData").text)))
   port = int(os.environ.get("PORT", 8000))
   app = create_app()
   app.run(host="0.0.0.0", port=port)

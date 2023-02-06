# py-myplace

Translation layer for exposing AdvantageAir MyPlace as simple REST API

copy and update config.json.original to config.json

test by running from main.py 

Install the HomeBridge plugin web thermostat (https://github.com/phenotypic/homebridge-web-thermostat)
Assumes configured zones are temp sensor enabled 
Sample config is

`{
    "accessory": "Thermostat",
    "name": "Lounge AC",
    "apiroute": "http://localhost:8000/zone/1",
    "temperatureDisplayUnits": 0,
    "pollInterval": 60
}`

copy and update py-myplace.service.orginal to py-myplace.service

when you are happy link py-myplace.service into /etc/systemd/system

run the below commands to run as a service and start at boot

sudo systemctl daemon-reload
sudo systemctl enable py-myplace.service

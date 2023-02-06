# py-myplace

Translation layer for exposing AdvantageAir MyPlace as simple REST API

Code expects to be cloned to /usr/local/bin/py-myplace/

Create the directory and then change its owner to pi.pi (chown pi.pi py-myplace) or what ever other account you want
it to run under, you will need to update py-myplace.service (and remember to do this each time you refresh from github)

update config.json to your local settings

test by running from cli 

when you are happy link py-myplace.service into /etc/systemd/system

ln -s /usr/local/bin/py-myplace/py-myplace.service /etc/systemd/system

run the below commands to run as a service and start at boot

sudo systemctl daemon-reload
sudo systemctl enable py-myplace.service




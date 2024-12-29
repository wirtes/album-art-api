#!/bin/bash
cd /home/pi/album-art-api/
export FLASK_APP=musicbrainz-api.py
/usr/bin/python3 -m flask run --host=0.0.0.0 --port=5005 > /home/pi/album-art-api/flask.log 2>&1

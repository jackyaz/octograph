#!/bin/sh

env >> /etc/environment

if [ -f /octograph/config/octograph.ini ]; then
	python /octograph/octopus_to_influxdb.py
else
	echo "/octograph/config/octograph.ini is missing"
	echo "Please copy /octograph/config/example-octograph.ini to /octograph/config/octograph.ini and customise with your information"
fi

exec cron -f -l 2

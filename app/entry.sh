#!/bin/sh

if [ -f /octograph/config/octograph.ini ]; then
	python /octograph/octopus_to_influxdb.py
else
	echo "/config/octograph.ini is missing, exiting"
	exit 1
fi

cron -f

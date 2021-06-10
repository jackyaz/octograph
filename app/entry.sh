#!/bin/sh

if [ -f /config/octograph.ini ]; then
	python /octograph/octopus_to_influxdb.py
else
	echo "/config/octograph.ini is missing, exiting"
	exit 1
fi

if [ -f /config/crontab ]; then
	cp /config/crontab /etc/cron.d/crontab
else
	echo "/config/crontab is missing, using default schedule"
	cp /octograph/crontab /etc/cron.d/crontab
fi

chmod 0644 /etc/cron.d/crontab
crontab /etc/cron.d/crontab
cron -f

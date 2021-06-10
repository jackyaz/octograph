Forked from: [https://github.com/stevenewey/octograph](https://github.com/stevenewey/octograph)
Steven's referral link for Octopus: [https://share.octopus.energy/vivid-emu-468](https://share.octopus.energy/vivid-emu-468)

[Speedtest CLI](https://www.speedtest.net/apps/cli)

Octograph
---------

Python tool for downloading energy consumption data from the
[Octopus Energy API](https://developer.octopus.energy/docs/api/) and loading it into [InfluxDB](https://www.influxdata.com/time-series-platform/influxdb/).

If you think you'd find this useful, but haven't switched to Octopus yet, then
you can follow my referrer link [https://share.octopus.energy/ashen-stone-712](https://share.octopus.energy/ashen-stone-712)

In the process, additional metrics will be generated and stored for unit rates
and costs as configured by the user. Suitable for fixed rate electricity and gas
tariffs.

Included is an example [Grafana](https://grafana.com) dashboard to visualise the captured data.

This fork assumes you have InfluxDB and Grafana deployed already.

.. image:: grafana-dashboard.png
   :width: 800

Installation
============

Tested on Ubuntu with Docker and Python 3.7.

Usage
=====

Create a configuration file ``octograph.ini`` customised with your Octopus
API key, meter details and energy rate information. This file should be in a
directory on the host that is mapped to /config in the Docker container.

By default, energy data for the previous day will be collected. Optional from
and to ranges may be specified to retrieve larger datasets. It is anticipated
that the script will be run daily by a cron job.

You should create an InfluxDB database ``energy``. The dashboard provided can
then be imported to review the data.

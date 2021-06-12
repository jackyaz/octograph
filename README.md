# Octograph
## Original author and credits
Forked from: [https://github.com/stevenewey/octograph](https://github.com/stevenewey/octograph)

Steven's referral link for Octopus: [https://share.octopus.energy/vivid-emu-468](https://share.octopus.energy/vivid-emu-468)

## About
Python tool for downloading energy consumption data from the
[Octopus Energy API](https://developer.octopus.energy/docs/api/) and loading it into [InfluxDB](https://www.influxdata.com/time-series-platform/influxdb/) and visualising in [Grafana](https://grafana.com).

If you think you'd find this useful, but haven't switched to Octopus yet, then you can follow my referrer link [https://share.octopus.energy/ashen-stone-712](https://share.octopus.energy/ashen-stone-712)

Suitable for fixed rate electricity and gas tariffs such as Octopus Fixed 24M Super Green tariff. Energy data for the previous hour will be collected, running every hour on the hour.

Included is an example Grafana dashboard to visualise the captured data.

This fork assumes you have InfluxDB and Grafana deployed already.

Tested on Ubuntu with Docker and Python 3.9.

## Usage
A Docker image for this app is available on [Docker Hub](https://hub.docker.com/r/jackyaz/octograph)

### docker cli
```bash
docker run -d \
  --name=octograph \
  -v /path/to/data:/octograph/config \
  --restart unless-stopped \
  jackyaz/octograph
```

### Parameters
The Docker images supports some parameters. These parameters are separated by a colon and indicate `<external>:<internal>` respectively. For example, `-v /apps/octograph:/octograph/config` would map ```/apps/octograph``` on the Docker host to ```/octograph/config``` inside the container, allowing you to edit the configuration file from outside the container.

| Parameter | Function |
| :----: | --- |
| `-v /octograph/config` | Local path for octograph configuration directory |

## Configuration
Create a copy of the example configuration file included in the image ```/octograph/config/example-octograph.ini``` and customise it with your Octopus API key, meter details and energy rate information then save it as ```/octograph/config/octograph.ini```

```nano``` is included in the container for editing the configuration file.

You should create an InfluxDB database ```energy```. The Grafana dashboard provided can be imported to visualise the data.

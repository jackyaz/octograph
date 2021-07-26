#!/usr/bin/env python

from configparser import ConfigParser
from urllib import parse
import click
import requests
from influxdb import InfluxDBClient
import time
import maya
from datetime import datetime, timedelta
import sys
import fileinput

errorcount = 0
maxerrorcount = 10

def retrieve_paginated_data(api_key, url, from_date, to_date, page=None):
    global errorcount
    args = {
        'period_from': from_date,
        'period_to': to_date,
    }
    if page:
        args['page'] = page

    response = None

    try:
        response = requests.get(url, params=args, auth=(api_key, ''))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        if errorcount <= maxerrorcount:
            errorcount = errorcount + 1
            click.echo(f'An error occurred when trying to contact Octopus API. Error details: {e}')
            click.echo(f'This is error {errorcount} of {maxerrorcount}. Waiting 60s and trying again')
            time.sleep(60)
            retrieve_paginated_data(
                api_key, url, from_date, to_date, page
            )
        else:
            raise click.ClickException('Persistent error when contacting Octopus API, please review error messages')

    data = {}

    try:
        data = response.json()
    except ValueError as e:
        if errorcount <= maxerrorcount:
            errorcount = errorcount + 1
            click.echo(f'An error occurred when trying to extract JSON payload from Octopus API. Error details: {e}')
            click.echo(f'This is error {errorcount} of {maxerrorcount}. Waiting 60s and trying again')
            time.sleep(60)
            retrieve_paginated_data(
                api_key, url, from_date, to_date, page
            )
        else:
            raise click.ClickException('Persistent error when contacting Octopus API, please review error messages')

    results = data.get('results', [])

    if data.get('next'):
        url_query = parse.urlparse(data.get('next')).query
        next_page = parse.parse_qs(url_query)['page'][0]
        results += retrieve_paginated_data(
            api_key, url, from_date, to_date, next_page
        )

    return results

def store_series(connection, series, metrics, rate_data):
    def active_rate_field(measurement):
        if series == 'gas':
            return 'unit_rate_gas'
        elif series == 'electricity':
            return 'unit_rate_electricity'

    def fields_for_measurement(measurement):
        consumption = measurement['consumption']
        if consumption == 16777.215:
            consumption = 0
        conversion_factor = rate_data.get('conversion_factor', None)
        if conversion_factor:
            consumption *= conversion_factor
        rate = active_rate_field(measurement)
        rate_cost = rate_data[rate]
        cost = consumption * rate_cost
        standing_charge = rate_data['standing_charge'] / 48  # 30 minute reads
        fields = {
            'consumption': consumption,
            'cost': cost,
            'total_cost': cost + standing_charge,
            'standing_charge': rate_data['standing_charge'],
            'unit_charge': rate_cost
        }
        return fields

    measurements = [
        {
            'measurement': series,
            'time': measurement['interval_end'],
            'fields': fields_for_measurement(measurement),
        }
        for measurement in metrics
    ]
    try:
        connection.write_points(measurements)
    except Exception as e:
        raise click.ClickException(f'Error when trying to save to InfluxDB, please review error messages: {e}')

@click.command()
@click.option('--hoursago', default=24, show_default=True)
def cmd(hoursago):
    config = ConfigParser()
    try:
        with open('/octograph/config/octograph.ini') as f:
            config.read_file(f)
    except IOError:
        raise click.ClickException('/octograph/config/octograph.ini is missing')

    influx = InfluxDBClient(
        host=config.get('influxdb', 'host', fallback='localhost'),
        port=config.getint('influxdb', 'port', fallback=8086),
        username=config.get('influxdb', 'user', fallback=''),
        password=config.get('influxdb', 'password', fallback=''),
        database=config.get('influxdb', 'database', fallback='energy'),
    )

    api_key = config.get('octopus', 'api_key')
    if not api_key:
        raise click.ClickException('No Octopus API key set')

    e_mpan = config.get('electricity', 'mpan', fallback=None)
    e_serial = config.get('electricity', 'serial_number', fallback=None)
    if not e_mpan or not e_serial:
        raise click.ClickException('No electricity meter identifiers')
    e_url = 'https://api.octopus.energy/v1/electricity-meter-points/' \
            f'{e_mpan}/meters/{e_serial}/consumption/'

    g_mpan = config.get('gas', 'mpan', fallback=None)
    g_serial = config.get('gas', 'serial_number', fallback=None)
    g_meter_type = config.get('gas', 'meter_type', fallback=1)
    g_vcf = config.get('gas', 'volume_correction_factor', fallback=1.02264)
    g_cv = config.get('gas', 'calorific_value', fallback=40)
    if not g_mpan or not g_serial:
        raise click.ClickException('No gas meter identifiers')
    g_url = 'https://api.octopus.energy/v1/gas-meter-points/' \
            f'{g_mpan}/meters/{g_serial}/consumption/'

    timezone = config.get('general', 'timezone', fallback='Europe/London')

    rate_data = {
        'electricity': {
            'standing_charge': config.getfloat(
                'electricity', 'standing_charge', fallback=0.0
            ),
            'unit_rate_electricity': config.getfloat(
                'electricity', 'unit_rate_electricity', fallback=0.0
            )
        },
        'gas': {
            'standing_charge': config.getfloat(
                'gas', 'standing_charge', fallback=0.0
            ),
            'unit_rate_gas': config.getfloat('gas', 'unit_rate_gas', fallback=0.0),
            # SMETS1 meters report kWh, SMET2 report m^3 and need converting to kWh first
            'conversion_factor': (float(g_vcf) * float(g_cv)) / 3.6 if int(g_meter_type) > 1 else None,
        }
    }

    from_iso = None
    to_iso = None

    firstruncompleted = config.get('firstrun', 'completed', fallback='none')

    if(firstruncompleted == 'none'):
        with open('/octograph/config/octograph.ini', 'a') as f:
            f.write('\n[firstrun]\ncompleted = false\n')
            firstruncompleted = 'false'

    if(firstruncompleted == 'true'):
        from_iso = maya.MayaDT.from_datetime(datetime.utcnow().replace(microsecond=0, second=0, minute=0) - timedelta(hours=hoursago)).datetime(to_timezone=timezone, naive=True).isoformat()
        to_iso = maya.MayaDT.from_datetime(datetime.utcnow().replace(microsecond=0, second=0, minute=0)).datetime(to_timezone=timezone, naive=True).isoformat()
    elif(firstruncompleted == 'false'):
        click.echo('Running first run import of all existing readings...')
        from_iso = maya.MayaDT.from_datetime(datetime.utcnow().replace(microsecond=0, second=0, minute=0) - timedelta(weeks=208)).datetime(to_timezone=timezone, naive=True).isoformat()
        to_iso = maya.MayaDT.from_datetime(datetime.utcnow().replace(microsecond=0, second=0, minute=0)).datetime(to_timezone=timezone, naive=True).isoformat()

    click.echo(f'Retrieving electricity data for {from_iso} until {to_iso}...')
    e_consumption = retrieve_paginated_data(
        api_key, e_url, from_iso, to_iso
    )
    click.echo(f'{len(e_consumption)} electricity readings retrieved.')
    store_series(influx, 'electricity', e_consumption, rate_data['electricity'])

    click.echo(
        f'Retrieving gas data for {from_iso} until {to_iso}...'
    )
    g_consumption = retrieve_paginated_data(
        api_key, g_url, from_iso, to_iso
    )
    click.echo(f'{len(g_consumption)} gas readings retrieved.')
    store_series(influx, 'gas', g_consumption, rate_data['gas'])

    if(firstruncompleted == 'false'):
        for line in fileinput.input('/octograph/config/octograph.ini', inplace=True):
            if line.strip().startswith('completed = '):
                line = 'completed = true\n'
            sys.stdout.write(line)

    with open('/etc/cron.d/crontab', 'r') as f:
        lines = f.readlines()
    with open('/etc/cron.d/crontab', 'w') as f:
        for line in lines:
            if line.strip('\n') != '0  *   *   *   *   /usr/local/bin/python3 /octograph/octopus_to_influxdb.py > /proc/1/fd/1 2>&1':
                f.write(line)

    if len(e_consumption) == 0 and len(g_consumption) == 0: 
        click.echo('0 readings detected, retrying hourly')
        with open('/etc/cron.d/crontab', 'a') as f:
            f.write('0  *   *   *   *   /usr/local/bin/python3 /octograph/octopus_to_influxdb.py > /proc/1/fd/1 2>&1') 

if __name__ == '__main__':
    cmd()

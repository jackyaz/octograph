FROM python:3.9-slim-buster
LABEL maintainer="Jack Yaz <jackyaz@outlook.com"

RUN apt-get update && apt-get -y install --no-install-recommends cron nano \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir 'requests >= 2.20.0'
RUN pip3 install --no-cache-dir 'influxdb == 5.2.0'
RUN pip3 install --no-cache-dir 'Click == 7.0'
RUN pip3 install --no-cache-dir 'maya == 0.5.0'

COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN crontab /etc/cron.d/crontab

COPY octopus_to_influxdb.py /octograph/
COPY example-octograph.ini /octograph/config/

COPY entry.sh /
RUN chmod 0755 /entry.sh

VOLUME /octograph/config

ENTRYPOINT ["/entry.sh"]

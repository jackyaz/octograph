FROM python:3.10.13-slim-bookworm
LABEL maintainer="Jack Yaz <jackyaz@outlook.com>"

RUN apt-get update && apt-get -y install --no-install-recommends cron nano procps \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install --no-cache-dir 'requests >= 2.20.0'
RUN pip3 install --no-cache-dir 'influxdb == 5.2.0'
RUN pip3 install --no-cache-dir 'Click >= 7.0'
RUN pip3 install --no-cache-dir 'pytz >= 2023.3'

COPY crontab /etc/crontab
RUN chmod 0644 /etc/crontab
RUN crontab /etc/crontab

COPY octopus_to_influxdb.py /octograph/
COPY example-octograph.ini /octograph/config/

COPY entry.sh /
RUN chmod 0755 /entry.sh

VOLUME /octograph/config

ENTRYPOINT ["/entry.sh"]

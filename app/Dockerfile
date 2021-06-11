FROM python:3.7
LABEL maintainer="Jack Yaz <jackyaz@outlook.com"

RUN apt-get update && apt-get -y install cron nano

RUN pip3 install --no-cache-dir 'requests >= 2.20.0'
RUN pip3 install --no-cache-dir 'influxdb == 5.2.0'
RUN pip3 install --no-cache-dir 'Click == 7.0'
RUN pip3 install --no-cache-dir 'maya == 0.5.0'

COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN crontab /etc/cron.d/crontab

COPY octopus_to_influxdb.py /octograph/

COPY entry.sh /
RUN chmod 0755 /entry.sh

ENTRYPOINT ["/entry.sh"]

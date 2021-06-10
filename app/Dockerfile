FROM python:3.7
LABEL maintainer="Jack Yaz <jackyaz@outlook.com"

RUN apt-get update && apt-get -y install cron nano

COPY requirements.txt /octograph/python/
RUN pip install --no-cache-dir -r /octograph/python/requirements.txt
COPY octopus_to_influxdb.py /octograph/

COPY entry.sh /
RUN chmod 0755 /entry.sh

ENTRYPOINT ["/entry.sh"]

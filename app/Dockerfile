FROM python:3.7
LABEL maintainer="Jack Yaz <jackyaz@outlook.com"

RUN apt-get update && apt-get -y install cron nano

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY octopus_to_influxdb.py ./

COPY entry.sh ./
RUN chmod 0755 ./entry.sh

ENTRYPOINT ["./entry.sh"]

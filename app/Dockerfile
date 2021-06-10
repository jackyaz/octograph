FROM python:3.7

LABEL maintainer="Jack Yaz <jackyaz@outlook.com"

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY octopus_to_influxdb.py ./

ENTRYPOINT [ "python", "./octopus_to_influxdb.py" ]

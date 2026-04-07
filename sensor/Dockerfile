FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /sensor

COPY requirements.txt ./
COPY sensor.py ./

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "sensor.py" ]
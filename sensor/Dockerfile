FROM python:3.11-slim

WORKDIR /sensor

COPY requirements.txt ./
COPY sensor.py ./

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "sensor.py" ]
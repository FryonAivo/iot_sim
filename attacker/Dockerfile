FROM python:3.11-slim

WORKDIR /attacker

COPY requirements.txt ./
COPY attacker.py ./

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "attacker.py" ]
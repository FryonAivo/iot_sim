import paho.mqtt.client as mqtt
import json
import time
import random

BROKER = "mosquitto"
TOPIC = "telemetry/sensor_01"

client = mqtt.Client()
client.username_pw_set('sensor', 'sensor')
client.connect(BROKER, 1883)

while True:
    # Simulating data
    data = {
        "device_id": "sensor_01",
        "temperature": round(random.uniform(20.0, 35.0), 2),
        "timestamp": int(time.time())
    }

    payload = json.dumps(data)
    client.publish(TOPIC, payload)
    print(f"Published: {payload}")
    time.sleep(5)
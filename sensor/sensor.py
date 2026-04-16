import paho.mqtt.client as mqtt
import random
import time

BROKER = "mosquitto"
PORT = 1883
DEVICE_ID = "sensor_01"
TOPIC = f"telemetry/{DEVICE_ID}"
USERNAME = "sensor"
PASSWORD = "sensor"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Connection failed: {reason_code}")
    else:
        print(f"Connected to {BROKER}:{PORT}")


def on_disconnect(client, userdata, flags, reason_code, properties):
    print(f"Disconnected: {reason_code}")


def on_publish(client, userdata, mid, reason_code, properties):
    if reason_code is not None and reason_code.is_failure:
        print(f"Publish failed for mid {mid}: {reason_code}")
    else:
        print(f"Message {mid} published")

# This is correct, I'm not sure why the linter doesn't like it      
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2) # type: ignore
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

try:
    while True:
        temp = round(random.uniform(20.0, 35.0), 2)
        payload = f'{{"device_id": "{DEVICE_ID}", "temperature": {temp}, "timestamp": {time.time()}}}'
        info = client.publish(TOPIC, payload, qos=1)
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            print(f"Publish error: {mqtt.error_string(info.rc)}")
        time.sleep(0.25)
except KeyboardInterrupt:
    print("Stopping publisher...")
finally:
    client.loop_stop()
    client.disconnect()
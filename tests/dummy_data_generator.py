import time
import json
import random
import paho.mqtt.publish as publish

BROKER = "127.0.0.1"
TOPIC = "fan_monitor/data"
SENSORS = ["Fan 1", "Fan 2", "Fan 3", "Fan 4", "Fan 5", "Extra 1", "Extra 2"]

def generate_data(detachment_event=False):
    base_pressure = 1450.0 if not detachment_event else 200.0
    return {
        sensor: {
            "pressure": base_pressure + random.uniform(-15.0, 15.0),
            "temperature": 22.0 + random.uniform(-0.5, 0.5)
        } for sensor in SENSORS
    }

if __name__ == "__main__":
    print("Publishing dummy telemetry. Press Ctrl+C to stop.")
    counter = 0
    try:
        while True:
            # Simulate a detachment event every 10 seconds
            is_detachment = (counter % 10 == 0 and counter > 0)
            payload = json.dumps(generate_data(is_detachment))
            try:
                publish.single(TOPIC, payload, hostname=BROKER)
                print(f"Published: {payload}")
            except ConnectionRefusedError:
                print("Connection refused. Make sure Mosquitto broker is running.")
            counter += 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("Generator stopped.")
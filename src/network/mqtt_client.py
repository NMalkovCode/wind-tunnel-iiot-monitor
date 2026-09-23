import json
import threading
import paho.mqtt.client as mqtt

class TelemetryReceiver:
    def __init__(self, broker, port, topic, ui_callback):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.ui_callback = ui_callback
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def start_daemon(self):
        self.client.connect(self.broker, self.port, 60)
        thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        thread.start()

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            client.subscribe(self.topic)
            print(f"Connected to Broker. Subscribed to {self.topic}")

    def _on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            for sensor_name, values in data.items():
                pressure = float(values.get("pressure", 0))
                temperature = float(values.get("temperature", 0))
                self.ui_callback(sensor_name, pressure, temperature)
        except Exception as e:
            print(f"Payload parsing error: {e}")
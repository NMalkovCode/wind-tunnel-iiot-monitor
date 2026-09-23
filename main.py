import json
from src.ui.app_window import FanMonitorApp
from src.network.mqtt_client import TelemetryReceiver
from src.processing.alert_logic import AlertEngine

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

class SystemController:
    def __init__(self):
        self.config = load_config()
        self.ui = FanMonitorApp(self.config)
        self.logic_engine = AlertEngine(window_size=self.config["SMA_WINDOW_SIZE"])
        
        self.network_listener = TelemetryReceiver(
            broker=self.config["MQTT_BROKER"],
            port=self.config["MQTT_PORT"],
            topic=self.config["MQTT_TOPIC"],
            ui_callback=self.safe_ui_update
        )

    def safe_ui_update(self, sensor_name, pressure, temperature):
        is_anomaly, current_sma, dp_dt = self.logic_engine.process_reading(sensor_name, pressure)
        # Bypassing the GIL constraint by queueing UI updates to the main thread
        self.ui.after(0, lambda: self.ui.update_sensor_display(sensor_name, current_sma, temperature, is_anomaly))

    def run(self):
        self.network_listener.start_daemon()
        self.ui.mainloop()

if __name__ == "__main__":
    app = SystemController()
    app.run()
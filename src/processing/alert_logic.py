import collections

class AlertEngine:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.sensor_buffers = collections.defaultdict(lambda: collections.deque(maxlen=window_size))
        self.previous_averages = collections.defaultdict(float)

    def process_reading(self, sensor_name, pressure_value):
        buffer = self.sensor_buffers[sensor_name]
        buffer.append(pressure_value)
        
        if len(buffer) < self.window_size:
            return False, pressure_value, 0.0

        current_sma = sum(buffer) / self.window_size
        prev_sma = self.previous_averages.get(sensor_name, current_sma)
        
        dp_dt = current_sma - prev_sma
        self.previous_averages[sensor_name] = current_sma

        # Belt detachment mathematical signature: rapid, sustained negative pressure gradient
        is_anomaly = dp_dt < -50.0

        return is_anomaly, current_sma, dp_dt
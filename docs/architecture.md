# How it works

The software is split into three small modules, each with one job, and `main.py` wires them
together.

```
 MQTT broker ── fan_monitor/data
      │
      ▼                                   ── background daemon thread ──
 TelemetryReceiver._on_message            src/network/mqtt_client.py
      │  one call per sensor
      ▼
 SystemController.safe_ui_update          main.py
      │
      ├─► AlertEngine.process_reading     src/processing/alert_logic.py
      │       → (is_anomaly, smoothed pressure, dP/dt)
      │
      │  ui.after(0, ...)  hands over to the GUI thread
      ▼                                   ── main thread ──
 FanMonitorApp.update_sensor_display      src/ui/app_window.py
```

## 1. Network: MQTT telemetry

[MQTT](https://mqtt.org/) is a lightweight publish/subscribe protocol designed for IIoT devices.
Publishers (the sensor reader on the Pi, a PLC or the simulator) send a JSON message to the topic
`fan_monitor/data` on a broker (Mosquitto on port 1883). The dashboard subscribes to that topic.

`TelemetryReceiver` connects to the broker and runs paho-mqtt's `loop_forever()` on a **daemon
thread**, so it never blocks the window and dies with the app. For each message it:

1. decodes the JSON payload into a dictionary of `{sensor_name: {"pressure": ..., "temperature": ...}}`;
2. reads each value with `.get(..., 0)`, so a missing or broken sensor gives 0 instead of a
   `KeyError` that would crash the monitor;
3. calls back into the controller once per sensor.

Any malformed payload is caught and logged to the console rather than stopping the listener.

## 2. Processing: the alert engine

`AlertEngine` keeps a separate rolling buffer (`collections.deque(maxlen=M)`) for every sensor.

### Smoothing: simple moving average

The wind tunnel is turbulent: local pressure can spike for a fraction of a second without anything
being wrong. Reacting to raw readings would mean constant false alarms. Each new reading is pushed
into the buffer (the oldest one drops out) and the average is recalculated:

$$y[n] = \frac{1}{M}\sum_{k=0}^{M-1} x[n-k]$$

where $x$ is the raw pressure and $M$ is `SMA_WINDOW_SIZE` (default 5). A larger $M$ is smoother
but reacts later; for a belt moving at 50 m/s, lag matters, so 5 samples was chosen as the balance
during testing. Until the buffer is full, the engine returns the raw value and never raises an
alert.

The 1 m silicone tubes between the pressure taps and the sensors do the same job physically: they
damp high-frequency fluctuations before they reach the sensor, so the software filter has less
noise to remove.

### Detection: the rate of change of pressure

A fixed "too low" threshold is easily tripped by buffeting and vortex shedding. A detachment has a
specific signature instead: the retention suction collapses quickly and stays collapsed, which is a
steep, **negative** rate of change of pressure. The engine approximates it with a backward
difference between consecutive smoothed values:

$$\frac{dP}{dt} \approx \frac{\bar P_t - \bar P_{t-1}}{\Delta t}$$

With one message per polling interval, $\Delta t$ is one sample, and the engine flags an anomaly
when the smoothed pressure falls by more than **50 Pa in one sample**. Rising pressure and slow
drift never trigger it.

`process_reading()` returns `(is_anomaly, smoothed_pressure, dP/dt)`.

## 3. User interface

`FanMonitorApp` is a fixed-size (990 × 540) CustomTkinter window with one panel per sensor:
Fan 1–5 (one per suction fan zone, see the [fan layout](hardware.md#sensor-placement)) and two
spare channels, Extra 1 and 2. Each panel shows the smoothed pressure in Pa and the temperature
in °C. When the alert engine flags a detachment, that zone's pressure turns **red** so operators
see where it is happening without reading numbers.

### Thread safety

Tkinter widgets may only be touched from the thread that created them. Updating a label straight
from the MQTT thread can corrupt the interface or crash it. So `SystemController.safe_ui_update`
does the maths on the network thread, then queues the actual label update onto the main thread's
event loop with `ui.after(0, lambda: ...)`. The network thread never waits on the GUI and the GUI
never waits on the network, which is why the dashboard stays responsive under continuous data.

## Simulator

`tests/dummy_data_generator.py` publishes a message for all 7 sensors once a second: about 1450 Pa
(±15 Pa noise) and 22 °C. Every 10th message the pressure drops to about 200 Pa, simulating a
detachment. With the default 5-sample window that is a fall in the average of about 250 Pa in one
step, well past the 50 Pa threshold.

## Versions

The version that ran in the tunnel during commissioning (listed in Appendix A of the report) was a
single script with operator-set From/To pressure limits and pop-up alerts. This repository is the
cleaned-up, modular version: networking, detection and interface are separate, settings live in
`config.json`, and the detection uses the moving-average and dP/dt method described in the report
instead of fixed limits.

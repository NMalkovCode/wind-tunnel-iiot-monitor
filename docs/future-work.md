# Future work

Ideas from the report for taking the project further.

## Reduce belt friction

The 1500 Pa ceiling comes from friction between the belt and the platen, not from the fans. Cutting
the friction would unlock the remaining 30% of fan power and allow higher-downforce models:
- an **air bearing**: pressurised air blown through micro-holes in the platen to float the belt on
  a thin film of air;
- **PTFE composite slip plates** on the platen to lower the friction coefficient.

## Machine learning at the edge

Replace the fixed dP/dt threshold with an anomaly detection model running on the Pi (with a USB
accelerator such as a Google Coral TPU): for example an Isolation Forest or an LSTM network. The
MQTT data logged by this system could be the training set, so the model learns each car model's
normal pressure and vibration pattern and warns before the threshold is ever reached.

## Many more sensors and a pressure map

The multiplexer design scales easily. A grid of 32 to 64 sensors across the whole belt would give a
live 2D pressure map (for example with PyQtGraph or Matplotlib) showing exactly where flow
separates or the diffuser stalls under the car. At that size the bus may need to move from I²C to
SPI for bandwidth.

## Flush-mounted sensors for research

The tubing is ideal for safety monitoring because it filters out fast fluctuations, but that rules
out research into fast, unsteady flow (vortex shedding from a front wing, wheel-wake turbulence).
For that, miniature MEMS sensors mounted flush in the platen, sampled at least twice as fast as the
fastest flow features (Nyquist), would remove the pneumatic lag entirely.

## Software

Smaller improvements to this codebase:
- log every reading to CSV or a database for later analysis;
- reconnect automatically if the broker connection drops;
- configurable sensor names and alert threshold in `config.json`;
- an audible alarm and an alert history panel.

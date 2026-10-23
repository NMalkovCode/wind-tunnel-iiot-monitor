# Results

The system was installed and tested in the B17 R.J. Mitchell Wind Tunnel at the University of
Southampton.

## System performance

| measure | result |
|---|---|
| Network latency (sensor change → broker → Pi) | consistently under 15 ms |
| Packet loss over the test window | none |
| Broker connection | no handshake failures; the only connection issue was getting the Pi whitelisted on the university network |
| Average CPU use (Pi 4) | ~18% |
| Peak memory | ~145 MB (under 4% of 4 GB) |
| CPU temperature | well below the 80 °C throttling limit, with only the case fan |
| GUI | no freezes, tearing or crashes under continuous data |

## Detecting a detachment

No model with enough downforce to lift the belt was available, so detachments were simulated by
removing the retention suction. Every simulated event produced the expected signature, a steep and
sustained pressure drop, and was flagged. Normal belt vibration and turbulence did not raise any
false alarms: the silicone tubing damped high-frequency noise physically and the moving average
removed what was left.

![Pressure during a detachment event](images/detachment-event.png)

## The facility's real limit: 1500 Pa

The second aim was to use the sensors to measure the tunnel itself. The suction fans were run up
step by step while the sensors recorded the retention pressure under the belt. Retention pressure
rises linearly with fan power and reaches **about 1500 Pa (15 mbar) at 70% fan power**, the
recommended maximum.

![Retention pressure vs fan power](images/retention-vs-fan-power.png)

Why stop at 70%? The fans have power to spare; the limit is **friction**. Suction under the belt
means atmospheric pressure presses the belt down onto the stainless-steel platen with a normal
force

$$F_N = \Delta P \times A$$

1500 Pa is about 153 kg per square metre of belt. The friction the drive motors must overcome is

$$F_f = \mu_k F_N$$

so it grows in step with the suction. Above 70% fan power the friction is more than the belt drive
motors can overcome and the belt stalls.

**What this means for testing:** the retention suction can never exceed about 1500 Pa, so a test is
only safe while the model's under-floor suction plus the tunnel's own static pressure drop stays
below that:

$$S > |L_{vehicle} + P_{tunnel}| \quad\text{with}\quad S_{max} \approx 1500\ \text{Pa}$$

If a model goes beyond it, turning the fans up does not help, because the belt would stall. This
gives the facility a clear, measured limit to share with clients (for example, by testing smaller
scale models of high-downforce cars).

## Measurement uncertainty

The digital sensors remove the main source of error in this kind of system, electrical noise on
analogue cables. The remaining errors were combined by root-sum-square:

$$U_{total} = \sqrt{U_{sensor}^2 + U_{thermal}^2 + U_{pneumatic}^2}$$

| source | uncertainty (±) |
|---|---|
| Sensor total error band (linearity, hysteresis, repeatability) | 1.0% |
| Residual thermal drift (fan motor heat, tunnel circulation) | 1.5% |
| Pneumatic lag and resonance in the 1 m tubes | 1.5% |
| Quantisation (24-bit ADC) | < 0.001%, negligible |
| Electromagnetic interference | eliminated by digital I²C |
| **Total** | **≈ 2.35%, about ±35 Pa at 1500 Pa** |

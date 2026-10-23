from src.processing.alert_logic import AlertEngine


def feed(engine, sensor, values):
    return [engine.process_reading(sensor, v) for v in values]


def test_warm_up_returns_raw_value_without_alert():
    engine = AlertEngine(window_size=5)
    for is_anomaly, value, dp_dt in feed(engine, "Fan 1", [1450, 1460, 1440, 1455]):
        assert not is_anomaly
        assert dp_dt == 0.0
    assert value == 1455


def test_moving_average_once_window_is_full():
    engine = AlertEngine(window_size=5)
    *_, (is_anomaly, sma, _) = feed(engine, "Fan 1", [1000, 1100, 1200, 1300, 1400])
    assert sma == 1200
    assert not is_anomaly


def test_steady_noisy_pressure_never_alerts():
    engine = AlertEngine(window_size=5)
    readings = [1450 + (15 if i % 2 else -15) for i in range(50)]
    assert not any(a for a, _, _ in feed(engine, "Fan 1", readings))


def test_sudden_pressure_loss_is_detected():
    engine = AlertEngine(window_size=5)
    feed(engine, "Fan 1", [1450] * 5)
    is_anomaly, sma, dp_dt = engine.process_reading("Fan 1", 200)
    assert is_anomaly
    assert sma == 1200
    assert dp_dt == -250


def test_pressure_rise_is_not_an_alert():
    engine = AlertEngine(window_size=5)
    feed(engine, "Fan 1", [200] * 5)
    is_anomaly, _, dp_dt = engine.process_reading("Fan 1", 1450)
    assert dp_dt > 0
    assert not is_anomaly


def test_drop_just_under_threshold_is_ignored():
    engine = AlertEngine(window_size=5)
    feed(engine, "Fan 1", [1450] * 5)
    # a 245 Pa drop in one sample moves a 5-sample average by 49 Pa
    is_anomaly, _, dp_dt = engine.process_reading("Fan 1", 1205)
    assert dp_dt == -49
    assert not is_anomaly


def test_sensors_are_tracked_independently():
    engine = AlertEngine(window_size=5)
    feed(engine, "Fan 1", [1450] * 5)
    feed(engine, "Fan 2", [1450] * 5)
    assert engine.process_reading("Fan 1", 200)[0]
    assert not engine.process_reading("Fan 2", 1450)[0]

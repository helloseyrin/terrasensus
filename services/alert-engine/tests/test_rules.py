from alert_engine.rules import evaluate


def test_moisture_critical_low():
    result = evaluate("moisture", 5.0)
    assert result is not None
    assert result["level"] == "critical"
    assert result["direction"] == "low"


def test_moisture_normal():
    result = evaluate("moisture", 40.0)
    assert result is None


def test_ec_critical_high():
    result = evaluate("ec", 3.5)
    assert result is not None
    assert result["level"] == "critical"
    assert result["direction"] == "high"


def test_unknown_sensor_returns_none():
    result = evaluate("unknown_sensor", 99.9)
    assert result is None

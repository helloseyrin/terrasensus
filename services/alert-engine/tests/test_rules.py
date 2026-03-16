"""
Tests for crop-aware threshold rules.
Each persona has its own test class to make failures immediately attributable.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rules import evaluate, get_thresholds


class TestGlobalDefaults:
    def test_moisture_critical_low(self):
        result = evaluate("moisture", 5.0)
        assert result["level"] == "critical"
        assert result["direction"] == "low"

    def test_moisture_normal(self):
        assert evaluate("moisture", 40.0) is None

    def test_ec_critical_high(self):
        result = evaluate("ec", 3.5)
        assert result["level"] == "critical"
        assert result["direction"] == "high"

    def test_unknown_sensor_returns_none(self):
        assert evaluate("unknown_sensor", 99.9) is None


class TestMykolaWheat:
    """
    Plot: Mykola's wheat field, Kherson Oblast, Ukraine.
    Chernozem soil, heavy N use, EC risk from synthetic fertiliser.
    """
    crop = "wheat"

    def test_wheat_higher_n_tolerance_than_global(self):
        # Wheat healthy N range is 50–160, global is 30–150
        # N=35 should be warning for wheat but fine for global default (low=30)
        result = evaluate("nitrogen", 35.0, crop=self.crop)
        assert result is not None
        assert result["direction"] == "low"

    def test_wheat_ec_higher_tolerance(self):
        # Wheat critical EC is 3.5 vs global 3.0
        # EC=3.2 is critical for global but only warning for wheat
        global_result = evaluate("ec", 3.2)
        wheat_result = evaluate("ec", 3.2, crop=self.crop)
        assert global_result["level"] == "critical"
        assert wheat_result["level"] == "warning"

    def test_wheat_normal_operating_range(self):
        assert evaluate("nitrogen", 120.0, crop=self.crop) is None
        assert evaluate("ph", 6.8, crop=self.crop) is None
        assert evaluate("ec", 0.9, crop=self.crop) is None


class TestFatimaCotton:
    """
    Plot: Fatima's cotton, Ferghana Valley, Uzbekistan.
    Arid desert soil, saline irrigation, EC already in warning range at baseline.
    """
    crop = "cotton"

    def test_cotton_tolerates_higher_ec(self):
        # Cotton critical EC is 5.0 vs global 3.0
        # EC=3.5 is critical globally but only warning for cotton
        global_result = evaluate("ec", 3.5)
        cotton_result = evaluate("ec", 3.5, crop=self.crop)
        assert global_result["level"] == "critical"
        assert cotton_result["level"] == "warning"

    def test_cotton_baseline_ec_is_warning(self):
        # Fatima's baseline EC=2.4 should be in warning range for cotton
        result = evaluate("ec", 2.4, crop=self.crop)
        assert result is not None
        assert result["level"] == "warning"
        assert result["direction"] == "high"

    def test_cotton_higher_temp_tolerance(self):
        # Cotton critical high temp is 42°C vs global 35°C
        assert evaluate("temperature", 38.0, crop=self.crop) is None
        result = evaluate("temperature", 38.0)   # global
        assert result is not None

    def test_cotton_alkaline_ph_acceptable(self):
        # Uzbekistan soil is naturally pH 7.9 — acceptable for cotton, warning for global
        global_result = evaluate("ph", 7.9)
        cotton_result = evaluate("ph", 7.9, crop=self.crop)
        assert global_result is not None        # global warns above 7.5
        assert cotton_result is None            # cotton is fine up to 8.0


class TestElenaVineyard:
    """
    Plot: Elena's Pinot Noir vineyard, Willamette Valley, Oregon.
    Volcanic soil, low N by design, maritime climate.
    Low N is intentional — excess N degrades wine quality.
    """
    crop = "pinot_noir"

    def test_vineyard_low_n_is_normal(self):
        # Elena's N=38 is BELOW global warning (low=30) but fine for vines (low=15)
        # This is the key test: global thresholds would falsely alarm on a healthy vineyard
        global_result = evaluate("nitrogen", 20.0)
        vine_result = evaluate("nitrogen", 20.0, crop=self.crop)
        assert global_result is not None        # global warns: below 30
        assert vine_result is None              # vineyard: 20 is fine (low=15)

    def test_vineyard_prefers_acidic_ph(self):
        # pH 6.1 is fine for Pinot Noir but would warn on global (low=5.5, but healthy low is 6.0)
        assert evaluate("ph", 6.1, crop=self.crop) is None

    def test_vineyard_stricter_ec(self):
        # Vines are salt-sensitive — EC critical is 2.0 vs global 3.0
        result = evaluate("ec", 2.2, crop=self.crop)
        assert result is not None
        assert result["level"] == "critical"

    def test_vineyard_baseline_all_normal(self):
        # Elena's baselines should all read as healthy for pinot_noir
        assert evaluate("ph", 6.1, crop=self.crop) is None
        assert evaluate("nitrogen", 38.0, crop=self.crop) is None
        assert evaluate("potassium", 145.0, crop=self.crop) is None
        assert evaluate("ec", 0.4, crop=self.crop) is None


class TestGetThresholds:
    def test_returns_global_for_unknown_crop(self):
        t = get_thresholds("unknown_crop")
        assert t["nitrogen"]["low"] == 30  # global default

    def test_returns_crop_override_for_pinot_noir(self):
        t = get_thresholds("pinot_noir")
        assert t["nitrogen"]["low"] == 15  # vineyard override

    def test_non_overridden_sensors_use_global(self):
        # Cotton doesn't override moisture — should get global value
        t = get_thresholds("cotton")
        assert t["moisture"]["critical_low"] == 10  # global

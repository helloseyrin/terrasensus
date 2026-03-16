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


class TestMykolaWatermelon:
    """
    Plot: Mykola's watermelon field, Kherson Oblast, Ukraine.
    Chernozem soil, Kherson watermelon variety. K-critical fruiting crop.
    N must be managed carefully — too high drives vine, not fruit.
    """
    crop = "watermelon"

    def test_watermelon_n_ceiling_lower_than_global(self):
        # N=160 is comfortably healthy globally (high=150 is close but critical_high=180)
        # For watermelon, N=160 is well above critical_high=120 — over-fertilisation
        global_result = evaluate("nitrogen", 110.0)
        watermelon_result = evaluate("nitrogen", 110.0, crop=self.crop)
        assert global_result is None                       # global: 110 is healthy (high=150)
        assert watermelon_result is not None               # watermelon: 110 is critical (critical_high=120)
        assert watermelon_result["direction"] == "high"

    def test_watermelon_cold_soil_alerts_earlier(self):
        # Watermelons need warm soil — critical below 8°C, global critical is 2°C
        # Temperature=10 is fine globally but is a warning for watermelon (low=16)
        global_result = evaluate("temperature", 10.0)
        watermelon_result = evaluate("temperature", 10.0, crop=self.crop)
        assert global_result is None                       # global: 10°C is healthy (low=5)
        assert watermelon_result is not None               # watermelon: 10°C is warning (low=16)

    def test_watermelon_k_low_alerts(self):
        # K=100 is healthy globally (low=80) but warning for watermelon (low=130)
        global_result = evaluate("potassium", 100.0)
        watermelon_result = evaluate("potassium", 100.0, crop=self.crop)
        assert global_result is None                       # global: 100 is healthy
        assert watermelon_result is not None               # watermelon: below K floor for fruit quality
        assert watermelon_result["direction"] == "low"

    def test_watermelon_baseline_all_normal(self):
        # Mykola's baselines should all read as healthy for watermelon
        assert evaluate("moisture", 44.0, crop=self.crop) is None
        assert evaluate("temperature", 22.0, crop=self.crop) is None
        assert evaluate("ph", 6.5, crop=self.crop) is None
        assert evaluate("nitrogen", 65.0, crop=self.crop) is None
        assert evaluate("potassium", 165.0, crop=self.crop) is None
        assert evaluate("ec", 0.8, crop=self.crop) is None


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

    def test_watermelon_n_ceiling_lower_than_global(self):
        t = get_thresholds("watermelon")
        assert t["nitrogen"]["critical_high"] == 120   # watermelon override
        assert get_thresholds()["nitrogen"]["critical_high"] == 180  # global default

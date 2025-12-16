import pandas as pd

from app.ingestion.drift import DriftDetector
from app.ingestion.normalization import SymbolNormalizer


def test_drift_detection_schema():
    detector = DriftDetector(expected_columns=["col1", "col2"])

    # Valid schema
    df_valid = pd.DataFrame({"col1": [1], "col2": [2]})
    assert detector.check_schema(df_valid) == []

    # Invalid schema
    df_invalid = pd.DataFrame({"col1": [1]})
    assert detector.check_schema(df_invalid) == ["col2"]

def test_drift_detection_quality():
    detector = DriftDetector(expected_columns=["col1"])

    # Good quality
    df_good = pd.DataFrame({"col1": [1, 2, 3, 4, 5]})
    assert detector.check_data_quality(df_good) == {}

    # Bad quality (more than 10% nulls)
    df_bad = pd.DataFrame({"col1": [1, None, None, None, None]})
    issues = detector.check_data_quality(df_bad)
    assert "col1" in issues
    assert issues["col1"] == 0.8

def test_symbol_normalization():
    normalizer = SymbolNormalizer()

    # Exact match
    assert normalizer.normalize("BTC") == "BTC"
    assert normalizer.normalize("btc") == "BTC"

    # Canonical map
    assert normalizer.normalize("bitcoin") == "BTC"
    assert normalizer.normalize("Ethereum") == "ETH"

    # Fuzzy match
    # "bitcion" -> "bitcoin" -> "BTC"
    # Note: My implementation maps input -> canonical directly if in map,
    # or fuzzy matches against keys. "bitcion" is close to "bitcoin".
    # Let's see if difflib catches "bitcion" as close to "bitcoin"
    assert normalizer.normalize("bitcion") == "BTC"

    # No match
    assert normalizer.normalize("random_coin_xyz") is None

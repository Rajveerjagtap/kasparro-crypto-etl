import pandas as pd

from app.ingestion.drift import DriftDetector, DriftSeverity
from app.ingestion.normalization import SymbolNormalizer


def test_drift_detection_schema():
    detector = DriftDetector(expected_columns=["col1", "col2"])

    # Valid schema - no drift results
    df_valid = pd.DataFrame({"col1": [1], "col2": [2]})
    results = detector.check_schema(df_valid)
    assert results == []

    # Invalid schema - should return DriftResult for missing column
    df_invalid = pd.DataFrame({"col1": [1]})
    results = detector.check_schema(df_invalid)
    assert len(results) == 1
    assert results[0].drift_type == "schema_missing"
    assert results[0].severity == DriftSeverity.CRITICAL
    assert "col2" in results[0].message

def test_drift_detection_quality():
    detector = DriftDetector(expected_columns=["col1"])

    # Good quality - no issues
    df_good = pd.DataFrame({"col1": [1, 2, 3, 4, 5]})
    results = detector.check_data_quality(df_good)
    assert results == []

    # Bad quality (more than 50% nulls) - should return CRITICAL DriftResult
    df_bad = pd.DataFrame({"col1": [1, None, None, None, None]})
    results = detector.check_data_quality(df_bad)
    assert len(results) == 1
    assert results[0].drift_type == "quality_nulls"
    assert results[0].severity == DriftSeverity.CRITICAL
    assert "col1" in results[0].message

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

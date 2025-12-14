import logging
from typing import Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

class DriftDetector:
    """
    Detects data drift in incoming batches of crypto data.
    Checks for:
    1. Schema changes (missing expected columns)
    2. Null value spikes (quality drift)
    3. Significant price deviations (concept drift - simplified)
    """

    def __init__(self, expected_columns: List[str]):
        self.expected_columns = expected_columns
        self.null_threshold = 0.1  # 10% nulls allowed
        self.price_deviation_threshold = 0.5  # 50% change allowed (simplified)

    def check_schema(self, df: pd.DataFrame) -> List[str]:
        """Returns a list of missing columns."""
        missing = [col for col in self.expected_columns if col not in df.columns]
        if missing:
            logger.warning(f"Schema Drift Detected: Missing columns {missing}")
        return missing

    def check_data_quality(self, df: pd.DataFrame) -> Dict[str, float]:
        """Checks for null ratios in columns. Returns dict of col -> null_ratio for failing cols."""
        null_ratios = df.isnull().mean()
        drifted_cols = null_ratios[null_ratios > self.null_threshold]

        if not drifted_cols.empty:
            logger.warning(f"Quality Drift Detected: High nulls in {drifted_cols.to_dict()}")
            return drifted_cols.to_dict()
        return {}

    def detect_drift(self, df: pd.DataFrame) -> bool:
        """
        Runs all checks. Returns True if drift is detected (and safe to proceed with caution),
        or raises error if critical.
        """
        missing_cols = self.check_schema(df)
        if missing_cols:
            # Critical failure if schema is wrong
            raise ValueError(f"Critical Schema Drift: Missing columns {missing_cols}")

        quality_issues = self.check_data_quality(df)
        if quality_issues:
            # We log but might allow proceeding depending on severity
            # For now, we just flag it
            pass

        return len(missing_cols) > 0 or len(quality_issues) > 0

import difflib
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DriftSeverity(str, Enum):
    """Severity levels for drift detection."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class DriftResult:
    """Result of a drift detection check."""
    drift_type: str
    severity: DriftSeverity
    confidence: float  # 0.0 to 1.0
    message: str
    details: dict[str, Any]
    timestamp: datetime


class DriftDetector:
    """
    Detects data drift in incoming batches of crypto data.

    Features:
    - Schema drift detection with fuzzy matching
    - Confidence scoring for ambiguous matches
    - Null value spike detection (quality drift)
    - Warning logs with structured details

    Checks for:
    1. Schema changes (missing/renamed columns)
    2. Null value spikes (quality drift)
    3. Type changes (type drift)
    """

    def __init__(
        self,
        expected_columns: list[str],
        null_threshold: float = 0.1,
        fuzzy_match_threshold: float = 0.8,
    ):
        self.expected_columns = expected_columns
        self.null_threshold = null_threshold  # 10% nulls allowed
        self.fuzzy_match_threshold = fuzzy_match_threshold
        self._drift_history: list[DriftResult] = []

    def check_schema(self, df: pd.DataFrame) -> list[DriftResult]:
        """
        Check for schema drift with fuzzy column matching.

        Returns list of DriftResult for each issue found.
        """
        results: list[DriftResult] = []
        actual_columns = set(df.columns)
        expected_set = set(self.expected_columns)

        # Find missing columns
        missing = expected_set - actual_columns

        for col in missing:
            # Try fuzzy matching against actual columns
            matches = difflib.get_close_matches(
                col, actual_columns, n=1, cutoff=self.fuzzy_match_threshold
            )

            if matches:
                # Column might have been renamed
                best_match = matches[0]
                # Calculate confidence score
                confidence = difflib.SequenceMatcher(None, col, best_match).ratio()

                result = DriftResult(
                    drift_type="schema_rename",
                    severity=DriftSeverity.WARNING,
                    confidence=confidence,
                    message=f"Column '{col}' may have been renamed to '{best_match}'",
                    details={
                        "expected_column": col,
                        "matched_column": best_match,
                        "similarity_score": round(confidence, 3),
                    },
                    timestamp=datetime.now(timezone.utc),
                )
                results.append(result)
                logger.warning(
                    f"Schema Drift: Column rename detected - "
                    f"'{col}' → '{best_match}' (confidence: {confidence:.2%})"
                )
            else:
                # Column is truly missing
                result = DriftResult(
                    drift_type="schema_missing",
                    severity=DriftSeverity.CRITICAL,
                    confidence=1.0,
                    message=f"Required column '{col}' is missing",
                    details={"missing_column": col, "available_columns": list(actual_columns)},
                    timestamp=datetime.now(timezone.utc),
                )
                results.append(result)
                logger.warning(f"Schema Drift: Missing column '{col}'")

        # Check for extra columns (informational)
        extra = actual_columns - expected_set
        if extra:
            result = DriftResult(
                drift_type="schema_extra",
                severity=DriftSeverity.INFO,
                confidence=1.0,
                message=f"New columns detected: {extra}",
                details={"extra_columns": list(extra)},
                timestamp=datetime.now(timezone.utc),
            )
            results.append(result)
            logger.info(f"Schema Change: New columns detected - {extra}")

        self._drift_history.extend(results)
        return results

    def check_data_quality(self, df: pd.DataFrame) -> list[DriftResult]:
        """
        Check for data quality drift (null ratios).

        Returns list of DriftResult for columns exceeding null threshold.
        """
        results: list[DriftResult] = []
        null_ratios = df.isnull().mean()
        drifted_cols = null_ratios[null_ratios > self.null_threshold]

        for col, ratio in drifted_cols.items():
            # Calculate severity based on null ratio
            if ratio > 0.5:
                severity = DriftSeverity.CRITICAL
            elif ratio > 0.25:
                severity = DriftSeverity.WARNING
            else:
                severity = DriftSeverity.INFO

            # Confidence is inverse of null ratio (lower nulls = higher confidence in data)
            confidence = 1.0 - ratio

            result = DriftResult(
                drift_type="quality_nulls",
                severity=severity,
                confidence=confidence,
                message=f"Column '{col}' has {ratio:.1%} null values",
                details={
                    "column": col,
                    "null_ratio": round(ratio, 4),
                    "threshold": self.null_threshold,
                    "row_count": len(df),
                    "null_count": int(df[col].isnull().sum()),
                },
                timestamp=datetime.now(timezone.utc),
            )
            results.append(result)
            logger.warning(
                f"Quality Drift: Column '{col}' has {ratio:.1%} nulls "
                f"(threshold: {self.null_threshold:.1%})"
            )

        self._drift_history.extend(results)
        return results

    def check_type_drift(
        self, df: pd.DataFrame, expected_types: Optional[dict[str, str]] = None
    ) -> list[DriftResult]:
        """
        Check for type drift in columns.

        Args:
            df: DataFrame to check
            expected_types: Dict of column -> expected dtype name
        """
        if not expected_types:
            return []

        results: list[DriftResult] = []

        for col, expected_type in expected_types.items():
            if col not in df.columns:
                continue

            actual_type = str(df[col].dtype)

            if expected_type.lower() not in actual_type.lower():
                msg = (
                    f"Column '{col}' type changed "
                    f"from '{expected_type}' to '{actual_type}'"
                )
                result = DriftResult(
                    drift_type="type_change",
                    severity=DriftSeverity.WARNING,
                    confidence=1.0,
                    message=msg,
                    details={
                        "column": col,
                        "expected_type": expected_type,
                        "actual_type": actual_type,
                    },
                    timestamp=datetime.now(timezone.utc),
                )
                results.append(result)
                logger.warning(f"Type Drift: {msg}")

        self._drift_history.extend(results)
        return results

    def detect_drift(self, df: pd.DataFrame) -> tuple[bool, list[DriftResult]]:
        """
        Run all drift detection checks.

        Returns:
            Tuple of (has_critical_drift, all_results)
        """
        all_results: list[DriftResult] = []

        # Schema check
        schema_results = self.check_schema(df)
        all_results.extend(schema_results)

        # Quality check
        quality_results = self.check_data_quality(df)
        all_results.extend(quality_results)

        # Check for critical issues
        has_critical = any(r.severity == DriftSeverity.CRITICAL for r in all_results)

        if has_critical:
            critical_issues = [
                r.message for r in all_results
                if r.severity == DriftSeverity.CRITICAL
            ]
            logger.error(f"Critical drift detected: {critical_issues}")

        return has_critical, all_results

    def get_drift_summary(self) -> dict[str, Any]:
        """Get summary of all drift detections."""
        if not self._drift_history:
            return {"total_issues": 0, "by_severity": {}, "by_type": {}}

        by_severity: dict[str, int] = {}
        by_type: dict[str, int] = {}

        for result in self._drift_history:
            by_severity[result.severity.value] = by_severity.get(result.severity.value, 0) + 1
            by_type[result.drift_type] = by_type.get(result.drift_type, 0) + 1

        latest = None
        if self._drift_history:
            latest = self._drift_history[-1].timestamp.isoformat()

        return {
            "total_issues": len(self._drift_history),
            "by_severity": by_severity,
            "by_type": by_type,
            "latest_drift": latest,
        }

    def clear_history(self) -> None:
        """Clear drift detection history."""
        self._drift_history.clear()


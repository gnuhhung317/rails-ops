"""
Tests asserting the integrity and correctness of the frozen Golden Path evidence
and ML score operational calibration artifact (docs/golden_path_evidence_artifact.json).
"""
import json
from pathlib import Path
import pytest

ARTIFACT_PATH = Path(__file__).resolve().parent.parent / "docs" / "golden_path_evidence_artifact.json"


@pytest.fixture(scope="module")
def artifact_data():
    """Loads and verifies the frozen golden path evidence artifact."""
    assert ARTIFACT_PATH.exists(), f"Artifact file does not exist at {ARTIFACT_PATH}"
    with open(ARTIFACT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict), "Artifact root must be a valid JSON dictionary"
    return data


def test_artifact_exists_and_is_valid_json(artifact_data):
    """Asserts that docs/golden_path_evidence_artifact.json exists and is valid JSON."""
    assert "training_baseline" in artifact_data, "Artifact missing 'training_baseline' section"
    assert (
        "checkpoints" in artifact_data or "milestones" in artifact_data
    ), "Artifact missing 'checkpoints' / 'milestones' section"


def test_training_baseline_properties(artifact_data):
    """
    Asserts that training_baseline contains required features,
    sample count > 10,000, and random_state=42.
    """
    baseline = artifact_data["training_baseline"]
    expected_features = ["DV_pressure", "H1", "Oil_temperature", "Motor_current", "TP3"]

    assert baseline["features"] == expected_features, (
        f"Features mismatch: expected {expected_features}, got {baseline['features']}"
    )
    assert baseline["sample_count"] > 10000, (
        f"Sample count must be > 10000, got {baseline['sample_count']}"
    )
    assert baseline["random_state"] == 42, (
        f"random_state must be 42, got {baseline['random_state']}"
    )
    assert baseline["contamination"] == 0.01, (
        f"contamination must be 0.01, got {baseline['contamination']}"
    )


def test_ml_corroborated_milestone(artifact_data):
    """
    Asserts that ml_corroborated milestone (2020-06-05 10:15:00) has
    operational_ml_score >= 0.35 and is_anomalous == True.
    """
    checkpoints = artifact_data.get("checkpoints", artifact_data.get("milestones", {}))
    assert "ml_corroborated" in checkpoints, "Milestone 'ml_corroborated' not found in artifact"

    ml_cp = checkpoints["ml_corroborated"]
    assert "10:15" in ml_cp["timestamp"], f"Unexpected timestamp: {ml_cp['timestamp']}"
    assert ml_cp["operational_ml_score"] >= 0.35, (
        f"operational_ml_score must be >= 0.35, got {ml_cp['operational_ml_score']}"
    )
    assert ml_cp["is_anomalous"] is True, "is_anomalous must be True for ml_corroborated"
    assert ml_cp["threshold"] == 0.35, "threshold must be 0.35"


def test_early_excursion_milestone(artifact_data):
    """
    Asserts that early_excursion milestone (2020-06-04 00:33:07) has
    operational_ml_score < 0.35 and is_anomalous == False.
    """
    checkpoints = artifact_data.get("checkpoints", artifact_data.get("milestones", {}))
    assert "early_excursion" in checkpoints, "Milestone 'early_excursion' not found in artifact"

    ee_cp = checkpoints["early_excursion"]
    assert ee_cp["timestamp"] == "2020-06-04 00:33:07", (
        f"Unexpected timestamp: {ee_cp['timestamp']}"
    )
    assert ee_cp["operational_ml_score"] < 0.35, (
        f"operational_ml_score must be < 0.35, got {ee_cp['operational_ml_score']}"
    )
    assert ee_cp["is_anomalous"] is False, "is_anomalous must be False for early_excursion"
    assert ee_cp["threshold"] == 0.35, "threshold must be 0.35"


def test_all_checkpoints_presence_and_calibration_consistency(artifact_data):
    """
    Verifies that all 5 key checkpoints are recorded and adhere to
    linear calibration invariants: raw_score == -raw_df and op_score == round(raw_score * 10, 4).
    """
    checkpoints = artifact_data.get("checkpoints", artifact_data.get("milestones", {}))
    required_checkpoints = [
        "early_excursion",
        "confirmed_degradation",
        "ml_corroborated",
        "lps_reactive",
        "post_maintenance",
    ]

    for cp_name in required_checkpoints:
        assert cp_name in checkpoints, f"Missing required checkpoint: {cp_name}"
        cp = checkpoints[cp_name]

        # Verify polarity inversion: raw_score == -raw_decision_function
        raw_df = cp["raw_decision_function"]
        raw_score = cp["raw_score"]
        assert pytest.approx(-raw_df, abs=1e-5) == raw_score, (
            f"Polarity inversion violated in {cp_name}: raw_score={raw_score}, -raw_df={-raw_df}"
        )

        # Verify operational linear scaling: op_score == round(raw_score * 10.0, 4)
        op_score = cp["operational_ml_score"]
        expected_op_score = round(raw_score * 10.0, 4)
        assert pytest.approx(expected_op_score, abs=1e-4) == op_score, (
            f"Operational scale factor 10.0 violated in {cp_name}: got {op_score}, expected {expected_op_score}"
        )

        # Verify is_anomalous consistency with threshold 0.35
        expected_anomalous = op_score > cp["threshold"]
        assert cp["is_anomalous"] == expected_anomalous, (
            f"is_anomalous inconsistency in {cp_name}: is_anomalous={cp['is_anomalous']}, op_score={op_score}"
        )

    # Post-maintenance recovery must be non-anomalous
    assert checkpoints["post_maintenance"]["is_anomalous"] is False
    assert checkpoints["post_maintenance"]["operational_ml_score"] < 0.35

    # LPS reactive alert must be anomalous
    assert checkpoints["lps_reactive"]["is_anomalous"] is True
    assert checkpoints["lps_reactive"]["operational_ml_score"] > 0.35

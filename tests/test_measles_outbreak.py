import os
import sys

# Add the project root to sys.path so models can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.measles_outbreak import run_model, build_sections, SCENARIO_LABELS


def test_run_model_default_params():
    params = {}
    results = run_model(params)
    assert "df_costs" in results
    df = results["df_costs"]
    assert list(df["Cost Type"]) == [
        "Hospitalization",
        "Lost productivity",
        "Contact tracing",
        "TOTAL",
    ]


def test_run_model_with_params():
    params = {
        "Cost of measles hospitalization": 10000,
        "Proportion of cases hospitalized": 0.1,
        "Hourly wage for worker": 25,
        "Hourly wage for contract tracer": 20,
        "Hours of contact tracing per contact": 2,
        "Number of contacts per case": 10,
        "Vaccination rate in community": 0.9,
        "Proportion of quarantine days that would be a missed day of work": 1.0,
        "Length of quarantine (days)": 21,
    }
    results = run_model(params)
    df = results["df_costs"]
    assert df.shape == (4, 4)


def test_run_model_label_overrides():
    params = {}
    overrides = {"22_cases": "Custom 22", "100_cases": "Custom 100", "803_cases": "Custom 803"}
    results = run_model(params, label_overrides=overrides)
    df = results["df_costs"]
    assert "Custom 22" in df.columns
    assert "Custom 100" in df.columns
    assert "Custom 803" in df.columns


def test_build_sections():
    params = {}
    results = run_model(params)
    sections = build_sections(results)
    assert len(sections) == 1
    assert sections[0]["title"] == "Measles Outbreak Costs"


def test_scenario_labels():
    assert "22_cases" in SCENARIO_LABELS
    assert "100_cases" in SCENARIO_LABELS
    assert "803_cases" in SCENARIO_LABELS

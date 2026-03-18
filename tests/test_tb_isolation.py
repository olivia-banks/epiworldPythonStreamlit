import os
import sys

# Add the project root to sys.path so models can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.tb_isolation import run_model, build_sections, SCENARIO_LABELS


def test_run_model_default_params():
    params = {}
    results = run_model(params)
    assert "df_infections" in results
    assert "df_costs" in results


def test_run_model_infections_columns():
    params = {}
    results = run_model(params)
    df = results["df_infections"]
    assert "Outcome" in df.columns
    assert list(df["Outcome"]) == ["Latent TB infections", "Active TB disease"]


def test_run_model_costs_columns():
    params = {}
    results = run_model(params)
    df = results["df_costs"]
    assert list(df["Cost Type"]) == [
        "Direct cost of isolation",
        "Lost productivity for index case",
        "Cost of secondary infections",
        "Total cost",
    ]


def test_run_model_label_overrides():
    params = {}
    overrides = {"14_day": "Custom 14-day", "5_day": "Custom 5-day"}
    results = run_model(params, label_overrides=overrides)
    df = results["df_costs"]
    assert "Custom 14-day" in df.columns
    assert "Custom 5-day" in df.columns


def test_build_sections():
    params = {}
    results = run_model(params)
    sections = build_sections(results)
    assert len(sections) == 2
    titles = [s["title"] for s in sections]
    assert "Number of Secondary Infections" in titles
    assert "Costs" in titles


def test_scenario_labels():
    assert "14_day" in SCENARIO_LABELS
    assert "5_day" in SCENARIO_LABELS


def test_run_model_with_params():
    params = {
        "Number of contacts for each released TB case": 10,
        "Probability that contact develops latent TB if 14-day isolation": 0.05,
        "Multiplier for infectiousness with 5-day vs. 14-day isolation": 1.5,
        "Hourly wage for worker": 25,
        "prob_latent_to_active_2yr": 0.1,
        "prob_latent_to_active_lifetime": 0.05,
        "cost_latent": 500,
        "cost_active": 20000,
        "isolation_type": 3,
        "Hourly wage for nurse": 40,
        "Time for nurse to check in w/ pt in motel or home (hrs)": 0.5,
        "discount_rate": 0.03,
        "remaining_years": 40,
    }
    results = run_model(params)
    df_costs = results["df_costs"]
    assert df_costs.shape == (4, 3)

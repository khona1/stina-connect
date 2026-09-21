from fastapi.testclient import TestClient

from api.server import app


client = TestClient(app)


def test_scenario_comparison_endpoint_returns_standard_scenarios():
    response = client.get("/scenarios/compare")

    assert response.status_code == 200

    data = response.json()
    assert list(data) == ["5K", "10K", "50K"]

    expected_metrics = {
        "ending_terminals",
        "exit_mrr",
        "exit_arr",
        "total_revenue",
        "total_deployment_capex",
        "total_profit",
        "profit_margin",
        "required_capital",
        "break_even_arpu",
    }

    assert set(data["5K"]) == expected_metrics
    assert data["10K"]["exit_arr"] > data["5K"]["exit_arr"]
    assert data["50K"]["exit_arr"] > data["10K"]["exit_arr"]

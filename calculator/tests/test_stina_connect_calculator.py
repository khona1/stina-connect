from stina_connect_calculator import (
    Inputs,
    calculate,
    compare_scenarios,
    standard_scenarios,
)


def test_base_case_matches_5000_terminal_scenario():
    result = calculate(Inputs(
        starting_terminals=5000,
        monthly_arpu=30,
        monthly_churn_rate=0,
        monthly_capacity_cost_per_terminal=9,
        monthly_support_cost_per_terminal=0,
        monthly_payment_cost_per_terminal=0,
        monthly_regulatory_cost_per_terminal=0,
        hardware_cost_per_terminal=0,
        installation_cost_per_terminal=0,
        initial_hardware_cost_per_terminal=0,
        initial_installation_cost_per_terminal=0,
    ))
    assert result["summary"]["ending_terminals"] == 5000
    assert result["summary"]["exit_mrr"] == 150000
    assert result["summary"]["exit_arr"] == 1800000
    assert result["summary"]["total_revenue"] == 1800000
    assert result["summary"]["total_profit"] == 1260000


def test_churn_reduces_terminal_base():
    result = calculate(Inputs(
        starting_terminals=1000,
        new_terminals_per_month=0,
        monthly_arpu=30,
        monthly_churn_rate=0.10,
        monthly_capacity_cost_per_terminal=0,
        monthly_support_cost_per_terminal=0,
        monthly_payment_cost_per_terminal=0,
        monthly_regulatory_cost_per_terminal=0,
        hardware_cost_per_terminal=0,
        installation_cost_per_terminal=0,
        initial_hardware_cost_per_terminal=0,
        initial_installation_cost_per_terminal=0,
    ))
    assert round(result["summary"]["ending_terminals"], 6) == 282.429536


def test_new_terminals_create_hardware_and_installation_cost():
    result = calculate(Inputs(
        starting_terminals=0,
        new_terminals_per_month=100,
        monthly_arpu=30,
        monthly_churn_rate=0,
        monthly_capacity_cost_per_terminal=0,
        monthly_support_cost_per_terminal=0,
        monthly_payment_cost_per_terminal=0,
        monthly_regulatory_cost_per_terminal=0,
        hardware_cost_per_terminal=400,
        installation_cost_per_terminal=50,
        initial_hardware_cost_per_terminal=0,
        initial_installation_cost_per_terminal=0,
    ))
    assert result["summary"]["new_terminals"] == 1200
    assert result["summary"]["hardware_and_installation"] == 540000
    assert result["summary"]["total_profit"] == -324000


def test_initial_deployment_capex_and_required_capital():
    result = calculate(Inputs(
        starting_terminals=1000,
        monthly_arpu=0,
        monthly_churn_rate=0,
        monthly_capacity_cost_per_terminal=0,
        monthly_support_cost_per_terminal=0,
        monthly_payment_cost_per_terminal=0,
        monthly_regulatory_cost_per_terminal=0,
        hardware_cost_per_terminal=0,
        installation_cost_per_terminal=0,
        initial_hardware_cost_per_terminal=400,
        initial_installation_cost_per_terminal=50,
    ))
    assert result["summary"]["initial_capex"] == 450000
    assert result["summary"]["required_capital"] == 450000


def test_standard_scenarios_have_5k_10k_50k():
    result = compare_scenarios(standard_scenarios())
    assert list(result) == ["5K", "10K", "50K"]
    assert result["5K"]["ending_terminals"] < 5000
    assert result["10K"]["exit_arr"] > result["5K"]["exit_arr"]
    assert result["50K"]["exit_arr"] > result["10K"]["exit_arr"]


def test_invalid_churn_is_rejected():
    try:
        calculate(Inputs(monthly_churn_rate=1.0))
    except ValueError as exc:
        assert "churn" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

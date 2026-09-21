"""STINA CONNECT financial model.

Pure-Python, dependency-free monthly scenario calculator.
All monetary values use the model currency supplied by the caller (USD by default).
This is a planning model, not a forecast.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Mapping


@dataclass(frozen=True)
class Inputs:
    starting_terminals: int = 5000
    new_terminals_per_month: int = 0
    monthly_arpu: float = 30.0
    monthly_churn_rate: float = 0.02
    monthly_capacity_cost_per_terminal: float = 9.0
    hardware_cost_per_terminal: float = 400.0
    installation_cost_per_terminal: float = 50.0
    initial_hardware_cost_per_terminal: float = 400.0
    initial_installation_cost_per_terminal: float = 50.0
    monthly_support_cost_per_terminal: float = 2.40
    monthly_payment_cost_per_terminal: float = 0.90
    monthly_regulatory_cost_per_terminal: float = 1.20
    fixed_monthly_operating_cost: float = 0.0
    months: int = 12


def _nonnegative(name: str, value: float) -> float:
    if value < 0:
        raise ValueError(f"{name} must be >= 0")
    return float(value)


def validate(inputs: Inputs) -> None:
    if inputs.starting_terminals < 0:
        raise ValueError("starting_terminals must be >= 0")
    if inputs.new_terminals_per_month < 0:
        raise ValueError("new_terminals_per_month must be >= 0")
    if not 0 <= inputs.monthly_churn_rate < 1:
        raise ValueError("monthly_churn_rate must be >= 0 and < 1")
    if inputs.months < 1 or inputs.months > 120:
        raise ValueError("months must be between 1 and 120")
    for name in (
        "monthly_arpu",
        "monthly_capacity_cost_per_terminal",
        "hardware_cost_per_terminal",
        "installation_cost_per_terminal",
        "initial_hardware_cost_per_terminal",
        "initial_installation_cost_per_terminal",
        "monthly_support_cost_per_terminal",
        "monthly_payment_cost_per_terminal",
        "monthly_regulatory_cost_per_terminal",
        "fixed_monthly_operating_cost",
    ):
        _nonnegative(name, getattr(inputs, name))


def calculate(inputs: Inputs) -> Dict:
    validate(inputs)

    active = float(inputs.starting_terminals)
    initial_capex = active * (
        inputs.initial_hardware_cost_per_terminal
        + inputs.initial_installation_cost_per_terminal
    )

    rows: List[Dict] = []
    total_revenue = 0.0
    total_variable_service_cost = 0.0
    total_hardware_cost = 0.0
    total_installation_cost = 0.0
    total_profit = 0.0
    total_churned = 0.0
    cumulative_cash = -initial_capex
    minimum_cumulative_cash = cumulative_cash

    for month in range(1, inputs.months + 1):
        churned = active * inputs.monthly_churn_rate
        active_after_churn = max(0.0, active - churned)
        added = float(inputs.new_terminals_per_month)
        ending_terminals = active_after_churn + added
        billable_terminals = (active_after_churn + ending_terminals) / 2.0

        revenue = billable_terminals * inputs.monthly_arpu
        capacity = billable_terminals * inputs.monthly_capacity_cost_per_terminal
        support = billable_terminals * inputs.monthly_support_cost_per_terminal
        payment = billable_terminals * inputs.monthly_payment_cost_per_terminal
        regulatory = billable_terminals * inputs.monthly_regulatory_cost_per_terminal
        fixed = inputs.fixed_monthly_operating_cost
        hardware = added * inputs.hardware_cost_per_terminal
        installation = added * inputs.installation_cost_per_terminal

        service_cost = capacity + support + payment + regulatory
        profit = revenue - service_cost - fixed - hardware - installation
        cumulative_cash += profit
        minimum_cumulative_cash = min(minimum_cumulative_cash, cumulative_cash)

        rows.append({
            "month": month,
            "starting_terminals": active,
            "churned_terminals": churned,
            "new_terminals": added,
            "ending_terminals": ending_terminals,
            "billable_terminals": billable_terminals,
            "revenue": revenue,
            "capacity_cost": capacity,
            "support_cost": support,
            "payment_cost": payment,
            "regulatory_cost": regulatory,
            "fixed_operating_cost": fixed,
            "hardware_cost": hardware,
            "installation_cost": installation,
            "service_cost": service_cost,
            "profit": profit,
            "cumulative_cash": cumulative_cash,
        })

        total_revenue += revenue
        total_variable_service_cost += service_cost
        total_hardware_cost += hardware
        total_installation_cost += installation
        total_profit += profit
        total_churned += churned
        active = ending_terminals

    exit_mrr = active * inputs.monthly_arpu
    total_deployment_capex = initial_capex + total_hardware_cost + total_installation_cost
    gross_service_contribution = total_revenue - total_variable_service_cost
    break_even_arpu = (
        (
            total_variable_service_cost
            + inputs.fixed_monthly_operating_cost * inputs.months
            + total_hardware_cost
            + total_installation_cost
            + initial_capex
        )
        / total_revenue
        * inputs.monthly_arpu
        if total_revenue
        else 0.0
    )

    return {
        "inputs": asdict(inputs),
        "summary": {
            "starting_terminals": inputs.starting_terminals,
            "ending_terminals": active,
            "total_churned_terminals": total_churned,
            "new_terminals": inputs.new_terminals_per_month * inputs.months,
            "total_revenue": total_revenue,
            "total_service_cost": total_variable_service_cost,
            "gross_service_contribution": gross_service_contribution,
            "gross_service_margin": (
                gross_service_contribution / total_revenue if total_revenue else 0.0
            ),
            "initial_capex": initial_capex,
            "hardware_and_installation": (
                total_hardware_cost + total_installation_cost
            ),
            "total_deployment_capex": total_deployment_capex,
            "total_profit": total_profit,
            "exit_mrr": exit_mrr,
            "exit_arr": exit_mrr * 12,
            "profit_margin": total_profit / total_revenue if total_revenue else 0.0,
            "break_even_arpu_per_billable_terminal": break_even_arpu,
            "required_capital": max(0.0, -minimum_cumulative_cash),
            "ending_cumulative_cash": cumulative_cash,
        },
        "months": rows,
    }


def compare_scenarios(
    scenarios: Mapping[str, Inputs],
) -> Dict[str, Dict]:
    """Run named scenarios and return compact side-by-side summaries."""
    result: Dict[str, Dict] = {}
    for name, inputs in scenarios.items():
        summary = calculate(inputs)["summary"]
        result[name] = {
            "ending_terminals": summary["ending_terminals"],
            "exit_mrr": summary["exit_mrr"],
            "exit_arr": summary["exit_arr"],
            "total_revenue": summary["total_revenue"],
            "total_deployment_capex": summary["total_deployment_capex"],
            "total_profit": summary["total_profit"],
            "profit_margin": summary["profit_margin"],
            "required_capital": summary["required_capital"],
            "break_even_arpu": summary["break_even_arpu_per_billable_terminal"],
        }
    return result


def standard_scenarios() -> Dict[str, Inputs]:
    """Default 5K/10K/50K STINA CONNECT comparison set."""
    common = dict(
        new_terminals_per_month=0,
        monthly_arpu=30.0,
        monthly_churn_rate=0.02,
        monthly_capacity_cost_per_terminal=9.0,
        hardware_cost_per_terminal=400.0,
        installation_cost_per_terminal=50.0,
        initial_hardware_cost_per_terminal=400.0,
        initial_installation_cost_per_terminal=50.0,
        monthly_support_cost_per_terminal=2.40,
        monthly_payment_cost_per_terminal=0.90,
        monthly_regulatory_cost_per_terminal=1.20,
        fixed_monthly_operating_cost=0.0,
        months=12,
    )
    return {
        "5K": Inputs(starting_terminals=5000, **common),
        "10K": Inputs(starting_terminals=10000, **common),
        "50K": Inputs(starting_terminals=50000, **common),
    }


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Run STINA CONNECT scenarios.")
    parser.add_argument("--input", help="JSON file containing Inputs fields.")
    parser.add_argument(
        "--scenarios",
        action="store_true",
        help="Print the standard 5K/10K/50K scenario comparison.",
    )
    args = parser.parse_args()

    if args.scenarios:
        print(json.dumps(compare_scenarios(standard_scenarios()), indent=2))
    else:
        values = {}
        if args.input:
            with open(args.input, "r", encoding="utf-8") as handle:
                values = json.load(handle)
        print(json.dumps(calculate(Inputs(**values)), indent=2))

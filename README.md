# STINA CONNECT

Network deployment economics and scenario planning for connectivity operators.

## What it does

STINA CONNECT models the financial economics of deploying connectivity terminals.

Core capabilities:

- 5,000 / 10,000 / 50,000 terminal scenarios
- Custom terminal deployments
- Editable ARPU
- Capacity cost modelling
- Churn modelling
- Hardware and installation CAPEX
- Monthly operating costs
- MRR and ARR
- Operating profit
- Profit margin
- Required capital
- Break-even ARPU
- Scenario comparison

## Architecture

The Python Scenario Engine is the single source of truth for financial calculations.

The web interface consumes the same model and must not duplicate financial formulas.

## Development

Run the scenario engine:

    python calculator/stina_connect_calculator.py --scenarios

Run tests:

    PYTHONPATH=calculator pytest -q

## Product direction

STINA CONNECT is intended to evolve from a deployment calculator into a commercial connectivity-planning product with:

- Interactive financial modelling
- Scenario comparison
- Reports
- Saved projects
- Team workflows
- API access
- Paid professional features

## Status

Early product build.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from calculator.stina_connect_calculator import Inputs, calculate, standard_scenarios


app = FastAPI(
    title="STINA CONNECT API",
    version="0.1.0",
    description="Network deployment economics and scenario planning API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CalculatorRequest(BaseModel):
    starting_terminals: int = Field(default=5000, ge=0)
    new_terminals_per_month: int = Field(default=0, ge=0)
    monthly_arpu: float = Field(default=30.0, ge=0)
    monthly_churn_rate: float = Field(default=0.02, ge=0, lt=1)
    monthly_capacity_cost_per_terminal: float = Field(default=9.0, ge=0)
    monthly_support_cost_per_terminal: float = Field(default=0.0, ge=0)
    monthly_payment_cost_per_terminal: float = Field(default=0.0, ge=0)
    monthly_regulatory_cost_per_terminal: float = Field(default=0.0, ge=0)
    fixed_monthly_operating_cost: float = Field(default=0.0, ge=0)
    hardware_cost_per_terminal: float = Field(default=400.0, ge=0)
    installation_cost_per_terminal: float = Field(default=50.0, ge=0)
    initial_hardware_cost_per_terminal: float = Field(default=400.0, ge=0)
    initial_installation_cost_per_terminal: float = Field(default=50.0, ge=0)
    months: int = Field(default=12, ge=1)


def to_inputs(request: CalculatorRequest) -> Inputs:
    return Inputs(**request.model_dump())


@app.get("/health")
def health():
    return {"status": "ok", "service": "stina-connect"}


@app.get("/scenarios")
def scenarios():
    return {
        name: calculate(inputs)["summary"]
        for name, inputs in standard_scenarios().items()
    }


@app.post("/calculate")
def calculate_endpoint(request: CalculatorRequest):
    try:
        result = calculate(to_inputs(request))
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

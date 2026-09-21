const API_URL = "http://127.0.0.1:8000";

const fields = [
  "starting_terminals",
  "new_terminals_per_month",
  "monthly_arpu",
  "monthly_churn_rate",
  "monthly_capacity_cost_per_terminal",
  "monthly_support_cost_per_terminal",
  "monthly_payment_cost_per_terminal",
  "monthly_regulatory_cost_per_terminal",
  "fixed_monthly_operating_cost",
  "hardware_cost_per_terminal",
  "installation_cost_per_terminal",
  "initial_hardware_cost_per_terminal",
  "initial_installation_cost_per_terminal",
  "months"
];

const defaults = {
  starting_terminals: 5000,
  new_terminals_per_month: 0,
  monthly_arpu: 30,
  monthly_churn_rate: 2,
  monthly_capacity_cost_per_terminal: 9,
  monthly_support_cost_per_terminal: 0,
  monthly_payment_cost_per_terminal: 0,
  monthly_regulatory_cost_per_terminal: 0,
  fixed_monthly_operating_cost: 0,
  hardware_cost_per_terminal: 400,
  installation_cost_per_terminal: 50,
  initial_hardware_cost_per_terminal: 400,
  initial_installation_cost_per_terminal: 50,
  months: 12
};

function value(id) {
  return Number(document.getElementById(id).value);
}

function payload() {
  return {
    starting_terminals: value("starting_terminals"),
    new_terminals_per_month: value("new_terminals_per_month"),
    monthly_arpu: value("monthly_arpu"),
    monthly_churn_rate: value("monthly_churn_rate") / 100,
    monthly_capacity_cost_per_terminal: value("monthly_capacity_cost_per_terminal"),
    monthly_support_cost_per_terminal: value("monthly_support_cost_per_terminal"),
    monthly_payment_cost_per_terminal: value("monthly_payment_cost_per_terminal"),
    monthly_regulatory_cost_per_terminal: value("monthly_regulatory_cost_per_terminal"),
    fixed_monthly_operating_cost: value("fixed_monthly_operating_cost"),
    hardware_cost_per_terminal: value("hardware_cost_per_terminal"),
    installation_cost_per_terminal: value("installation_cost_per_terminal"),
    initial_hardware_cost_per_terminal: value("initial_hardware_cost_per_terminal"),
    initial_installation_cost_per_terminal: value("initial_installation_cost_per_terminal"),
    months: value("months")
  };
}

function money(number) {
  return new Intl.NumberFormat("en-ZA", {
    style: "currency",
    currency: "ZAR",
    maximumFractionDigits: 0
  }).format(number);
}

function number(number) {
  return new Intl.NumberFormat("en-ZA", {
    maximumFractionDigits: 0
  }).format(number);
}

function percent(number) {
  return `${(number * 100).toFixed(1)}%`;
}

function set(id, text) {
  document.getElementById(id).textContent = text;
}

function render(summary) {
  set("exit_arr", money(summary.exit_arr));
  set("exit_mrr", money(summary.exit_mrr));
  set("total_revenue", money(summary.total_revenue));
  set("total_deployment_capex", money(summary.total_deployment_capex));
  set("total_profit", money(summary.total_profit));
  set("profit_margin", percent(summary.profit_margin));
  set("required_capital", money(summary.required_capital));
  set("break_even_arpu", money(summary.break_even_arpu_per_billable_terminal));
  set("ending_terminals", number(summary.ending_terminals));
  set("new_terminals", number(summary.new_terminals));
  set("hardware_and_installation", money(summary.hardware_and_installation));
}

async function calculate() {
  const error = document.getElementById("error");
  const loading = document.getElementById("loading");

  error.textContent = "";
  loading.classList.remove("hidden");

  try {
    const response = await fetch(`${API_URL}/calculate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload())
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Calculation failed");
    }

    render(data.summary);
  } catch (err) {
    error.textContent = err.message;
  } finally {
    loading.classList.add("hidden");
  }
}

function setDefaults(overrides = {}) {
  const values = { ...defaults, ...overrides };

  for (const id of fields) {
    if (values[id] !== undefined) {
      document.getElementById(id).value = values[id];
    }
  }

  calculate();
}

document.getElementById("calculate").addEventListener("click", calculate);

document.querySelectorAll("[data-preset]").forEach(button => {
  button.addEventListener("click", () => {
    const terminals = Number(button.dataset.preset);
    setDefaults({
      starting_terminals: terminals
    });
  });
});

calculate();

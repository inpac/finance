import math
import copy
from datetime import date, timedelta


def months_to_payoff(balance: float, apr: float, monthly_payment: float) -> int:
    if balance <= 0:
        return 0
    r = apr / 12
    if r == 0:
        return math.ceil(balance / monthly_payment) if monthly_payment > 0 else 9999
    if monthly_payment <= balance * r:
        return 9999
    return math.ceil(-math.log(1 - (balance * r) / monthly_payment) / math.log(1 + r))


def total_interest_cost(balance: float, apr: float, monthly_payment: float) -> float:
    months = months_to_payoff(balance, apr, monthly_payment)
    if months >= 9999:
        return float("inf")
    return monthly_payment * months - balance


def _payoff_schedule(debts_input: list, extra_monthly: float, sort_key: str) -> list:
    debts = [
        {
            "id": d["id"],
            "label": d["label"],
            "balance": d["principal_balance"],
            "apr": d["interest_rate_annual"],
            "min_payment": d["minimum_payment"],
            "extra": 0.0,
        }
        for d in debts_input
        if d["principal_balance"] > 0
    ]

    if sort_key == "apr":
        debts.sort(key=lambda x: x["apr"], reverse=True)
    else:
        debts.sort(key=lambda x: x["balance"])

    results = []
    month = 0
    today = date.today()
    freed_payment = 0.0

    while any(d["balance"] > 0 for d in debts) and month < 600:
        month += 1
        available_extra = extra_monthly + freed_payment
        freed_this_month = 0.0

        for i, d in enumerate(debts):
            if d["balance"] <= 0:
                continue
            is_focus = i == next((j for j, x in enumerate(debts) if x["balance"] > 0), -1)
            payment = d["min_payment"] + (available_extra if is_focus else 0)
            interest = d["balance"] * (d["apr"] / 12)
            principal_paid = min(payment - interest, d["balance"])
            d["balance"] = max(0.0, d["balance"] - principal_paid)
            if d["balance"] == 0:
                freed_this_month += d["min_payment"]
                payoff_date = today + timedelta(days=month * 30)
                results.append({
                    "label": d["label"],
                    "payoff_month": month,
                    "payoff_date": payoff_date.strftime("%b %Y"),
                })

        freed_payment += freed_this_month

    return results


def avalanche_schedule(debts: list, extra_monthly: float = 0) -> list:
    return _payoff_schedule(debts, extra_monthly, sort_key="apr")


def snowball_schedule(debts: list, extra_monthly: float = 0) -> list:
    return _payoff_schedule(debts, extra_monthly, sort_key="balance")


def consumption_vs_generating(debts: list) -> dict:
    consumption = [d for d in debts if d["debt_nature"] == "consumption"]
    generating = [d for d in debts if d["debt_nature"] == "income_generating"]
    return {
        "consumption_balance": sum(d["principal_balance"] for d in consumption),
        "consumption_monthly_cost": sum(d["minimum_payment"] for d in consumption),
        "generating_balance": sum(d["principal_balance"] for d in generating),
        "generating_income": sum(d["income_generated"] for d in generating),
        "consumption_count": len(consumption),
        "generating_count": len(generating),
    }

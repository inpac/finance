import models.income as income_model
import models.expense as expense_model
import models.debt as debt_model
import models.credit_card as cc_model
import models.investment as inv_model
from config import HIGH_INTEREST_THRESHOLD


def debt_to_income(person_id: int) -> float:
    gross = income_model.total_gross_monthly(person_id)
    if gross <= 0:
        return 0.0
    debt_pay = debt_model.total_minimum_payments(person_id)
    cc_pay = sum(r["min_payment"] for r in cc_model.list_by_person(person_id))
    return (debt_pay + cc_pay) / gross


def expense_ratio(person_id: int) -> float:
    gross = income_model.total_gross_monthly(person_id)
    if gross <= 0:
        return 0.0
    return expense_model.total_monthly(person_id) / gross


def credit_utilization_overall(person_id: int) -> float:
    total_limit = cc_model.total_limit(person_id)
    if total_limit <= 0:
        return 0.0
    return cc_model.total_balance(person_id) / total_limit


def passive_income_ratio(person_id: int) -> float:
    expenses = expense_model.total_monthly(person_id)
    if expenses <= 0:
        return 0.0
    passive = income_model.total_passive_monthly(person_id)
    inv_income = inv_model.total_income_monthly(person_id)
    debt_income = debt_model.total_income_generated(person_id)
    return (passive + inv_income + debt_income) / expenses


def high_interest_debt_total(person_id: int) -> float:
    debts = debt_model.list_by_person(person_id)
    cards = cc_model.list_by_person(person_id)
    total = sum(d["principal_balance"] for d in debts if d["interest_rate_annual"] > HIGH_INTEREST_THRESHOLD)
    total += sum(c["current_balance"] for c in cards if c["interest_rate"] > HIGH_INTEREST_THRESHOLD)
    return total


def fi_progress(person_id: int, portfolio_value: float, annual_expenses: float,
                swr: float = 0.04) -> float:
    if annual_expenses <= 0:
        return 0.0
    fi_target = annual_expenses / swr
    return min(portfolio_value / fi_target, 1.0)


def scorecard(person_id: int, portfolio_value: float = 0) -> dict:
    dti = debt_to_income(person_id)
    er = expense_ratio(person_id)
    cu = credit_utilization_overall(person_id)
    pir = passive_income_ratio(person_id)
    annual_exp = expense_model.total_monthly(person_id) * 12
    fi_pct = fi_progress(person_id, portfolio_value, annual_exp)
    hi_debt = high_interest_debt_total(person_id)

    return {
        "debt_to_income": dti,
        "dti_status": "good" if dti < 0.36 else "warning" if dti < 0.50 else "critical",
        "expense_ratio": er,
        "er_status": "good" if er < 0.50 else "warning" if er < 0.70 else "critical",
        "credit_utilization": cu,
        "cu_status": "good" if cu < 0.30 else "warning" if cu < 0.50 else "critical",
        "passive_income_ratio": pir,
        "pir_status": "excellent" if pir >= 1.0 else "good" if pir >= 0.5 else "growing" if pir > 0 else "none",
        "fi_progress": fi_pct,
        "high_interest_debt": hi_debt,
    }

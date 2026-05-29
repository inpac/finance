import models.income as income_model
import models.expense as expense_model
import models.debt as debt_model
import models.credit_card as cc_model
import models.investment as inv_model


def monthly_net_income(person_id: int) -> float:
    return income_model.total_net_monthly(person_id)


def monthly_expenses(person_id: int) -> float:
    return expense_model.total_monthly(person_id)


def monthly_debt_payments(person_id: int) -> float:
    return debt_model.total_minimum_payments(person_id) + cc_model.total_balance(person_id) * 0  # min payments only


def monthly_cash_flow(person_id: int) -> float:
    net = monthly_net_income(person_id)
    exp = monthly_expenses(person_id)
    debt_pay = debt_model.total_minimum_payments(person_id)
    cc_pay = sum(r["min_payment"] for r in cc_model.list_by_person(person_id))
    return net - exp - debt_pay - cc_pay


def savings_rate(person_id: int) -> float:
    gross = income_model.total_gross_monthly(person_id)
    if gross <= 0:
        return 0.0
    flow = monthly_cash_flow(person_id)
    return flow / gross


def monthly_investment_contributions(person_id: int) -> float:
    return inv_model.total_monthly_contribution(person_id)


def summary(person_id: int) -> dict:
    gross = income_model.total_gross_monthly(person_id)
    net = income_model.total_net_monthly(person_id)
    exp = monthly_expenses(person_id)
    debt_pay = debt_model.total_minimum_payments(person_id)
    cc_pay = sum(r["min_payment"] for r in cc_model.list_by_person(person_id))
    flow = net - exp - debt_pay - cc_pay
    return {
        "gross_income": gross,
        "net_income": net,
        "expenses": exp,
        "debt_payments": debt_pay + cc_pay,
        "cash_flow": flow,
        "savings_rate": flow / gross if gross > 0 else 0.0,
    }

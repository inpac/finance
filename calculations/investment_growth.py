import math
from config import SAFE_WITHDRAWAL_RATE, DEFAULT_MARKET_RETURN


def future_value(pv: float, annual_rate: float, years: int, monthly_contribution: float = 0) -> float:
    r = annual_rate / 12
    n = years * 12
    fv_lump = pv * (1 + r) ** n
    if r > 0:
        fv_annuity = monthly_contribution * (((1 + r) ** n - 1) / r)
    else:
        fv_annuity = monthly_contribution * n
    return fv_lump + fv_annuity


def npv(annual_rate: float, cashflows: list[float]) -> float:
    r = annual_rate / 12
    return sum(cf / (1 + r) ** t for t, cf in enumerate(cashflows))


def cagr(beginning: float, ending: float, years: float) -> float:
    if beginning <= 0 or years <= 0:
        return 0.0
    return (ending / beginning) ** (1 / years) - 1


def time_to_fi(annual_expenses: float, portfolio_value: float,
               annual_contribution: float,
               expected_return: float = DEFAULT_MARKET_RETURN,
               swr: float = SAFE_WITHDRAWAL_RATE) -> int:
    fi_target = annual_expenses / swr
    if portfolio_value >= fi_target:
        return 0
    pv = portfolio_value
    for year in range(1, 101):
        pv = pv * (1 + expected_return) + annual_contribution
        if pv >= fi_target:
            return year
    return 100


def projection_table(pv: float, annual_rate: float, monthly_contribution: float,
                     horizons: list[int] = None) -> list[dict]:
    if horizons is None:
        horizons = [1, 5, 10, 20, 30]
    rows = []
    for y in horizons:
        fv = future_value(pv, annual_rate, y, monthly_contribution)
        gain = fv - pv - monthly_contribution * y * 12
        rows.append({"years": y, "future_value": fv, "gain_from_returns": gain})
    return rows

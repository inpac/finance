import json
import models.person as person_model
import models.income as income_model
import models.expense as expense_model
import models.debt as debt_model
import models.credit_card as cc_model
import models.investment as inv_model
import models.asset as asset_model
import calculations.cash_flow as cf
import calculations.net_worth as nw
import calculations.financial_ratios as ratios
import calculations.investment_growth as ig

SYSTEM_PROMPT = """You are an elite personal financial independence advisor. Your sole mission is to guide each person toward FINANCIAL INDEPENDENCE through a strict hierarchy:

1. MAXIMIZE INCOME — Identify every untapped income stream. Prioritize passive, scalable, and income-generating assets. If a person's income is 100% salary, call it out explicitly and provide 3 concrete alternatives suited to their profile.

2. MINIMIZE EXPENSES TO REALISTIC FLOORS — Never suggest impossible austerity. Instead compute the gap between current spending and the realistic_minimum provided for each category. Show exactly how much cash is freed monthly.

3. ELIMINATE HIGH-INTEREST CONSUMPTION DEBT URGENTLY — Credit card and personal loan debt above 10% APR is financial cancer. Always recommend the avalanche method. Never recommend investing while carrying >10% APR consumption debt (exception: employer 401k match).

4. GROW INCOME-GENERATING ASSETS — Mortgages on rental properties, business loans with positive ROI — these are tools. The goal: passive_income ≥ total_expenses (Financial Independence).

RESPONSE FORMAT — always follow this structure:
## FINANCIAL SNAPSHOT
- Net Worth: $X | Monthly Cash Flow: $X | FI Progress: X%
- Passive Income Ratio: X% (target: 100%)
- Key Alert: [most critical issue in one sentence]

## TOP 5 PRIORITY ACTIONS
For each action: [#] ACTION | Monthly Impact: +/-$X | Difficulty: Easy/Medium/Hard | Timeline: X months

## DETAILED ANALYSIS
[detailed section per topic requested, with exact numbers from the user's data]

## FI TIMELINE
Based on current trajectory vs. optimized trajectory.

IMPORTANT RULES:
- Every statement must cite the user's actual numbers. Never give generic advice.
- Be direct, even blunt. Financial sugar-coating costs people years of their life.
- If no API key is available, still provide analysis based on the data given.
- Amounts in the user's currency unless stated otherwise.
- Highlight income-generating debt separately from consumption debt.
"""


def build_snapshot(person_id: int) -> str:
    person = person_model.get(person_id)
    if not person:
        return "Person not found."

    incomes = income_model.list_by_person(person_id)
    expenses = expense_model.list_by_person(person_id)
    debts = debt_model.list_by_person(person_id)
    cards = cc_model.list_by_person(person_id)
    investments = inv_model.list_by_person(person_id)
    assets = asset_model.list_by_person(person_id)

    cf_data = cf.summary(person_id)
    nw_data = nw.summary(person_id)
    portfolio = inv_model.total_value(person_id)
    annual_exp = expense_model.total_monthly(person_id) * 12
    score = ratios.scorecard(person_id, portfolio)

    lines = [
        f"=== FINANCIAL PROFILE: {person['name']} ===",
        f"Currency: {person['currency']}",
        "",
        "--- INCOME STREAMS ---",
    ]
    for i in incomes:
        net = i["amount_monthly"] * (1 - i["tax_rate"])
        lines.append(f"  [{i['category'].upper()}] {i['label']}: ${i['amount_monthly']:,.0f}/mo gross | ${net:,.0f}/mo net | tax rate {i['tax_rate']*100:.0f}%")
    lines += [
        f"  TOTAL GROSS: ${cf_data['gross_income']:,.0f}/mo | TOTAL NET: ${cf_data['net_income']:,.0f}/mo",
        "",
        "--- EXPENSES ---",
    ]
    for e in expenses:
        lean = e["realistic_minimum"]
        savings = (e["amount_monthly"] - lean) if lean is not None else 0
        lean_note = f" | lean min: ${lean:,.0f} (save ${savings:,.0f}/mo)" if lean is not None else ""
        ess = "essential" if e["is_essential"] else "optional"
        lines.append(f"  [{e['category'].upper()} / {e['expense_type']}] {e['label']}: ${e['amount_monthly']:,.0f}/mo [{ess}]{lean_note}")
    lines += [
        f"  TOTAL EXPENSES: ${cf_data['expenses']:,.0f}/mo",
        f"  LEAN BUDGET TOTAL: ${expense_model.total_lean_monthly(person_id):,.0f}/mo",
        "",
        "--- DEBTS ---",
    ]
    for d in debts:
        nature_tag = "INCOME-GENERATING" if d["debt_nature"] == "income_generating" else "CONSUMPTION"
        income_note = f" | generates ${d['income_generated']:,.0f}/mo" if d["income_generated"] > 0 else ""
        lines.append(f"  [{nature_tag}] {d['label']} ({d['debt_type']}): balance ${d['principal_balance']:,.2f} | APR {d['interest_rate_annual']*100:.1f}% | min payment ${d['minimum_payment']:,.0f}/mo{income_note}")
    lines += [
        f"  TOTAL DEBT BALANCE: ${nw_data['debts']:,.0f}",
        f"  TOTAL MIN PAYMENTS: ${cf_data['debt_payments']:,.0f}/mo",
        "",
        "--- CREDIT CARDS ---",
    ]
    for c in cards:
        util = c["current_balance"] / c["credit_limit"] * 100 if c["credit_limit"] > 0 else 0
        lines.append(f"  {c['card_name']} ({c['issuer'] or ''}): balance ${c['current_balance']:,.0f} / limit ${c['credit_limit']:,.0f} ({util:.0f}% util) | APR {c['interest_rate']*100:.1f}% | min ${c['min_payment']:,.0f}/mo")
    lines += [
        "",
        "--- INVESTMENTS ---",
    ]
    for inv in investments:
        gain = inv["current_value"] - (inv["cost_basis"] or inv["current_value"])
        lines.append(f"  [{inv['asset_class'].upper()}] {inv['label']}: ${inv['current_value']:,.0f} current value | +${inv['monthly_contribution']:,.0f}/mo contribution | {inv['expected_annual_return']*100:.1f}% exp. return | income ${inv['income_monthly']:,.0f}/mo")
    lines += [
        f"  TOTAL PORTFOLIO: ${nw_data['investments']:,.0f}",
        "",
        "--- PHYSICAL ASSETS ---",
    ]
    for a in assets:
        lines.append(f"  [{a['asset_type'].upper()}] {a['label']}: ${a['current_value']:,.0f}")
    lines += [
        f"  TOTAL PHYSICAL ASSETS: ${nw_data['physical_assets']:,.0f}",
        "",
        "--- KEY METRICS ---",
        f"  Net Worth: ${nw_data['net_worth']:,.0f}",
        f"  Monthly Cash Flow: ${cf_data['cash_flow']:,.0f}",
        f"  Savings Rate: {score['expense_ratio']*100:.1f}% of gross goes to expenses",
        f"  Debt-to-Income Ratio: {score['debt_to_income']*100:.1f}% [{score['dti_status'].upper()}]",
        f"  Credit Utilization: {score['credit_utilization']*100:.1f}% [{score['cu_status'].upper()}]",
        f"  Passive Income Ratio: {score['passive_income_ratio']*100:.1f}% of expenses covered by passive income [{score['pir_status'].upper()}]",
        f"  FI Progress: {score['fi_progress']*100:.1f}% toward Financial Independence",
        f"  High-Interest Debt (>10% APR): ${score['high_interest_debt']:,.0f}",
    ]

    return "\n".join(lines)

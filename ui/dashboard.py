from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich import box

from ui.console import console
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
from config import DEFAULT_MARKET_RETURN, SAFE_WITHDRAWAL_RATE


def _status_color(status: str) -> str:
    return {"good": "green", "warning": "yellow", "critical": "red",
            "excellent": "bright_green", "growing": "cyan", "none": "red"}.get(status, "white")


def _bar(ratio: float, width: int = 20) -> str:
    filled = round(min(ratio, 1.0) * width)
    return "█" * filled + "░" * (width - filled)


def show_dashboard(person_id: int):
    person = person_model.get(person_id)
    if not person:
        console.print("[critical]Persona no encontrada[/critical]")
        return

    cf_data = cf.summary(person_id)
    nw_data = nw.summary(person_id)
    portfolio = inv_model.total_value(person_id)
    annual_exp = expense_model.total_monthly(person_id) * 12
    score = ratios.scorecard(person_id, portfolio)

    incomes = income_model.list_by_person(person_id)
    expenses = expense_model.list_by_person(person_id)
    debts = debt_model.list_by_person(person_id)
    cards = cc_model.list_by_person(person_id)
    investments = inv_model.list_by_person(person_id)
    assets = asset_model.list_by_person(person_id)

    console.rule(f"[header] DASHBOARD FINANCIERO: {person['name'].upper()} [/header]")
    console.print()

    # ── Header KPIs ──
    fi_pct = score["fi_progress"] * 100
    fi_bar = _bar(score["fi_progress"], 30)
    flow_color = "green" if cf_data["cash_flow"] >= 0 else "red"
    nw_color = "green" if nw_data["net_worth"] >= 0 else "red"

    kpi_text = (
        f"  Patrimonio Neto: [{'money' if nw_data['net_worth'] >= 0 else 'debt'}]${nw_data['net_worth']:,.0f}[/]   "
        f"Flujo Mensual: [{flow_color}]${cf_data['cash_flow']:+,.0f}[/{flow_color}]   "
        f"Progreso IF: [cyan]{fi_pct:.1f}%[/cyan]\n"
        f"  [cyan]{fi_bar}[/cyan] {fi_pct:.1f}% hacia Independencia Financiera"
    )
    console.print(Panel(kpi_text, title="[bold]RESUMEN EJECUTIVO[/bold]", border_style="blue"))
    console.print()

    # ── Income panel ──
    inc_table = Table(box=box.SIMPLE, show_header=True, padding=(0, 1))
    inc_table.add_column("Fuente", style="bold")
    inc_table.add_column("Categoría")
    inc_table.add_column("Neto/mes", justify="right")
    for i in incomes:
        net = i["amount_monthly"] * (1 - i["tax_rate"])
        cat_style = "green" if i["category"] in ("passive", "rental", "business") else "white"
        inc_table.add_row(i["label"], Text(i["category"], style=cat_style), f"${net:,.0f}")
    inc_table.add_row("─" * 20, "", "─" * 10)
    inc_table.add_row("[bold]TOTAL NETO[/bold]", "", f"[bold green]${cf_data['net_income']:,.0f}[/bold green]")

    # ── Expenses panel ──
    exp_table = Table(box=box.SIMPLE, show_header=True, padding=(0, 1))
    exp_table.add_column("Gasto", style="bold")
    exp_table.add_column("Tipo")
    exp_table.add_column("Actual/mes", justify="right")
    exp_table.add_column("Lean", justify="right")
    for e in expenses[:8]:
        lean_str = f"${e['realistic_minimum']:,.0f}" if e["realistic_minimum"] is not None else "-"
        ess_style = "white" if e["is_essential"] else "yellow"
        exp_table.add_row(Text(e["label"], style=ess_style), e["expense_type"], f"${e['amount_monthly']:,.0f}", lean_str)
    exp_table.add_row("─" * 20, "", "─" * 10, "─" * 8)
    lean_total = expense_model.total_lean_monthly(person_id)
    exp_table.add_row("[bold]TOTAL[/bold]", "", f"[bold red]${cf_data['expenses']:,.0f}[/bold red]", f"[green]${lean_total:,.0f}[/green]")

    console.print(Columns([
        Panel(inc_table, title=f"[bold green]INGRESOS[/bold green] (${cf_data['gross_income']:,.0f} bruto)", border_style="green"),
        Panel(exp_table, title=f"[bold red]GASTOS[/bold red]", border_style="red"),
    ]))

    # ── Debts panel ──
    debt_table = Table(box=box.SIMPLE, show_header=True, padding=(0, 1))
    debt_table.add_column("Deuda", style="bold")
    debt_table.add_column("Naturaleza")
    debt_table.add_column("Balance", justify="right")
    debt_table.add_column("APR", justify="right")
    debt_table.add_column("Pago min.", justify="right")
    for d in debts:
        nat_style = "green" if d["debt_nature"] == "income_generating" else "red"
        apr_style = "red" if d["interest_rate_annual"] > 0.10 else "yellow"
        debt_table.add_row(
            d["label"],
            Text(d["debt_nature"][:10], style=nat_style),
            f"${d['principal_balance']:,.0f}",
            Text(f"{d['interest_rate_annual']*100:.1f}%", style=apr_style),
            f"${d['minimum_payment']:,.0f}",
        )

    # ── Credit cards panel ──
    cc_table = Table(box=box.SIMPLE, show_header=True, padding=(0, 1))
    cc_table.add_column("Tarjeta", style="bold")
    cc_table.add_column("Utilización")
    cc_table.add_column("Balance", justify="right")
    cc_table.add_column("APR", justify="right")
    for c in cards:
        util = c["current_balance"] / c["credit_limit"] if c["credit_limit"] > 0 else 0
        util_style = "red" if util > 0.50 else "yellow" if util > 0.30 else "green"
        bar = _bar(util, 12)
        cc_table.add_row(
            c["card_name"],
            Text(f"{bar} {util*100:.0f}%", style=util_style),
            f"${c['current_balance']:,.0f}",
            f"{c['interest_rate']*100:.1f}%",
        )

    console.print(Columns([
        Panel(debt_table, title=f"[bold red]DEUDAS[/bold red] (${nw_data['debts']:,.0f} total)", border_style="red"),
        Panel(cc_table, title=f"[bold yellow]TARJETAS[/bold yellow]", border_style="yellow"),
    ]))

    # ── Investments + Net Worth ──
    inv_table = Table(box=box.SIMPLE, show_header=True, padding=(0, 1))
    inv_table.add_column("Inversión", style="bold")
    inv_table.add_column("Clase")
    inv_table.add_column("Valor", justify="right")
    inv_table.add_column("Ingreso/mes", justify="right")
    for inv in investments:
        inc_str = f"[green]${inv['income_monthly']:,.0f}[/green]" if inv["income_monthly"] > 0 else "-"
        inv_table.add_row(inv["label"], inv["asset_class"], f"${inv['current_value']:,.0f}", inc_str)
    inv_table.add_row("─" * 20, "", "─" * 10, "─" * 8)
    total_inv_income = inv_model.total_income_monthly(person_id)
    inv_table.add_row("[bold]TOTAL[/bold]", "", f"[bold green]${nw_data['investments']:,.0f}[/bold green]", f"[green]${total_inv_income:,.0f}/mo[/green]")

    # Scorecard
    sc = score
    def _sc_row(label, val_str, status):
        color = _status_color(status)
        return f"  {label}: [{color}]{val_str}[/{color}] [{color}]{status.upper()}[/{color}]"

    sc_lines = [
        _sc_row("DTI", f"{sc['debt_to_income']*100:.1f}%", sc["dti_status"]),
        _sc_row("Utilización CC", f"{sc['credit_utilization']*100:.1f}%", sc["cu_status"]),
        _sc_row("Ingreso Pasivo/Gastos", f"{sc['passive_income_ratio']*100:.1f}%", sc["pir_status"]),
        _sc_row("Gastos/Ingreso", f"{sc['expense_ratio']*100:.1f}%", sc["er_status"]),
        f"  Deuda alto interés (>10%): [red]${sc['high_interest_debt']:,.0f}[/red]",
        "",
        f"  FV portfolio a 10 años: [cyan]${ig.future_value(portfolio, DEFAULT_MARKET_RETURN, 10, inv_model.total_monthly_contribution(person_id)):,.0f}[/cyan]",
    ]

    console.print(Columns([
        Panel(inv_table, title=f"[bold cyan]INVERSIONES[/bold cyan]", border_style="cyan"),
        Panel("\n".join(sc_lines), title="[bold]SCORECARD FINANCIERO[/bold]", border_style="white"),
    ]))
    console.print()

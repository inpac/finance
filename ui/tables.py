from rich.table import Table
from rich.text import Text
from rich import box


def _money(val: float, color: str = "green") -> Text:
    return Text(f"${val:,.2f}", style=f"bold {color}")


def _pct(val: float) -> str:
    return f"{val*100:.1f}%"


def persons_table(rows) -> Table:
    t = Table(title="Personas", box=box.ROUNDED, show_lines=True)
    t.add_column("ID", style="muted", width=4)
    t.add_column("Nombre", style="bold")
    t.add_column("Email")
    t.add_column("Moneda")
    for r in rows:
        t.add_row(str(r["id"]), r["name"], r["email"] or "-", r["currency"])
    return t


def incomes_table(rows) -> Table:
    t = Table(title="Ingresos", box=box.ROUNDED, show_lines=True)
    t.add_column("ID", style="muted", width=4)
    t.add_column("Descripción", style="bold")
    t.add_column("Categoría")
    t.add_column("Bruto/mes", justify="right")
    t.add_column("Impuesto", justify="right")
    t.add_column("Neto/mes", justify="right")
    for r in rows:
        net = r["amount_monthly"] * (1 - r["tax_rate"])
        cat_color = "green" if r["category"] in ("passive", "rental", "business") else "white"
        t.add_row(
            str(r["id"]),
            r["label"],
            Text(r["category"], style=cat_color),
            _money(r["amount_monthly"]),
            _pct(r["tax_rate"]),
            _money(net),
        )
    return t


def expenses_table(rows) -> Table:
    t = Table(title="Gastos", box=box.ROUNDED, show_lines=True)
    t.add_column("ID", style="muted", width=4)
    t.add_column("Descripción", style="bold")
    t.add_column("Categoría")
    t.add_column("Tipo")
    t.add_column("Actual/mes", justify="right")
    t.add_column("Mínimo Lean", justify="right")
    t.add_column("Ahorro pot.", justify="right")
    for r in rows:
        lean = r["realistic_minimum"]
        savings = (r["amount_monthly"] - lean) if lean is not None else 0
        ess_style = "white" if r["is_essential"] else "yellow"
        t.add_row(
            str(r["id"]),
            Text(r["label"], style=ess_style),
            r["category"],
            r["expense_type"],
            _money(r["amount_monthly"], "red"),
            _money(lean) if lean is not None else Text("-", style="muted"),
            _money(savings, "green") if savings > 0 else Text("-", style="muted"),
        )
    return t


def debts_table(rows) -> Table:
    t = Table(title="Deudas", box=box.ROUNDED, show_lines=True)
    t.add_column("ID", style="muted", width=4)
    t.add_column("Descripción", style="bold")
    t.add_column("Tipo")
    t.add_column("Naturaleza")
    t.add_column("Balance", justify="right")
    t.add_column("APR", justify="right")
    t.add_column("Pago min.", justify="right")
    t.add_column("Ingreso gen.", justify="right")
    for r in rows:
        nature_style = "green" if r["debt_nature"] == "income_generating" else "red"
        apr_style = "red" if r["interest_rate_annual"] > 0.10 else "yellow" if r["interest_rate_annual"] > 0.05 else "green"
        t.add_row(
            str(r["id"]),
            r["label"],
            r["debt_type"],
            Text(r["debt_nature"], style=nature_style),
            _money(r["principal_balance"], "red"),
            Text(_pct(r["interest_rate_annual"]), style=apr_style),
            _money(r["minimum_payment"], "red"),
            _money(r["income_generated"], "green") if r["income_generated"] > 0 else Text("-", style="muted"),
        )
    return t


def credit_cards_table(rows) -> Table:
    t = Table(title="Tarjetas de Crédito", box=box.ROUNDED, show_lines=True)
    t.add_column("ID", style="muted", width=4)
    t.add_column("Tarjeta", style="bold")
    t.add_column("Emisor")
    t.add_column("Balance", justify="right")
    t.add_column("Límite", justify="right")
    t.add_column("Utilización", justify="right")
    t.add_column("APR", justify="right")
    t.add_column("Pago min.", justify="right")
    for r in rows:
        util = r["current_balance"] / r["credit_limit"] if r["credit_limit"] > 0 else 0
        util_style = "red" if util > 0.50 else "yellow" if util > 0.30 else "green"
        apr_style = "red" if r["interest_rate"] > 0.10 else "green"
        util_bar = _utilization_bar(util)
        t.add_row(
            str(r["id"]),
            r["card_name"],
            r["issuer"] or "-",
            _money(r["current_balance"], "red"),
            _money(r["credit_limit"]),
            Text(f"{util_bar} {util*100:.0f}%", style=util_style),
            Text(_pct(r["interest_rate"]), style=apr_style),
            _money(r["min_payment"], "red"),
        )
    return t


def investments_table(rows) -> Table:
    t = Table(title="Inversiones", box=box.ROUNDED, show_lines=True)
    t.add_column("ID", style="muted", width=4)
    t.add_column("Descripción", style="bold")
    t.add_column("Clase")
    t.add_column("Valor actual", justify="right")
    t.add_column("Contribución/mes", justify="right")
    t.add_column("Retorno esp.", justify="right")
    t.add_column("Ingreso/mes", justify="right")
    for r in rows:
        t.add_row(
            str(r["id"]),
            r["label"],
            r["asset_class"],
            _money(r["current_value"]),
            _money(r["monthly_contribution"]),
            _pct(r["expected_annual_return"]),
            _money(r["income_monthly"], "green") if r["income_monthly"] > 0 else Text("-", style="muted"),
        )
    return t


def assets_table(rows) -> Table:
    t = Table(title="Activos Físicos", box=box.ROUNDED, show_lines=True)
    t.add_column("ID", style="muted", width=4)
    t.add_column("Descripción", style="bold")
    t.add_column("Tipo")
    t.add_column("Valor actual", justify="right")
    t.add_column("Precio compra", justify="right")
    t.add_column("Deprecia?")
    for r in rows:
        dep = Text("Sí", style="yellow") if r["depreciates"] else Text("No", style="green")
        t.add_row(
            str(r["id"]),
            r["label"],
            r["asset_type"],
            _money(r["current_value"]),
            _money(r["purchase_price"]) if r["purchase_price"] else Text("-", style="muted"),
            dep,
        )
    return t


def payoff_table(schedule: list, method: str) -> Table:
    t = Table(title=f"Plan de Pago — {method}", box=box.ROUNDED)
    t.add_column("Deuda", style="bold")
    t.add_column("Meses", justify="right")
    t.add_column("Fecha estimada", justify="right")
    for i, item in enumerate(schedule):
        t.add_row(
            item["label"],
            str(item["payoff_month"]),
            item["payoff_date"],
        )
    return t


def projection_table_render(rows: list, pv: float) -> Table:
    t = Table(title="Proyección de Inversión", box=box.ROUNDED)
    t.add_column("Horizonte", justify="right")
    t.add_column("Valor Futuro", justify="right")
    t.add_column("Ganancia por retornos", justify="right")
    t.add_column("Múltiplo", justify="right")
    for r in rows:
        mult = r["future_value"] / pv if pv > 0 else 0
        t.add_row(
            f"{r['years']} años",
            _money(r["future_value"]),
            _money(r["gain_from_returns"]),
            f"{mult:.1f}x",
        )
    return t


def _utilization_bar(ratio: float, width: int = 10) -> str:
    filled = round(ratio * width)
    return "█" * filled + "░" * (width - filled)

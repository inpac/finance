from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.panel import Panel

from ui.console import console
from ui.forms import ask, ask_float, ask_int, ask_choice, ask_bool, ask_percent
from ui import tables as tbl
from ui.dashboard import show_dashboard

import models.person as person_model
import models.income as income_model
import models.expense as expense_model
import models.debt as debt_model
import models.credit_card as cc_model
import models.investment as inv_model
import models.asset as asset_model
import calculations.debt_payoff as payoff
import calculations.investment_growth as ig
import calculations.net_worth as nw
import calculations.cash_flow as cf

# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────
_current_person_id: int | None = None
_current_person_name: str = ""


def get_current_person() -> int | None:
    return _current_person_id


def _require_person() -> bool:
    if _current_person_id is None:
        console.print("[warning]Primero selecciona una persona (opción 1)[/warning]")
        return False
    return True


# ─────────────────────────────────────────────
# PERSONS
# ─────────────────────────────────────────────
def menu_persons():
    global _current_person_id, _current_person_name
    while True:
        console.rule("[info]PERSONAS[/info]")
        persons = person_model.list_all()
        if persons:
            console.print(tbl.persons_table(persons))
        choices = ["1", "2", "3", "4", "0"]
        console.print("\n[1] Seleccionar persona  [2] Crear  [3] Editar  [4] Eliminar  [0] Volver")
        opt = Prompt.ask("Opción", choices=choices, default="0")
        if opt == "0":
            break
        elif opt == "1":
            if not persons:
                console.print("[warning]No hay personas. Crea una primero.[/warning]")
                continue
            pid = ask_int("ID de la persona")
            p = person_model.get(pid)
            if p:
                _current_person_id = pid
                _current_person_name = p["name"]
                console.print(f"[good]Persona activa: {p['name']}[/good]")
            else:
                console.print("[critical]ID no encontrado[/critical]")
        elif opt == "2":
            name = ask("Nombre completo")
            email = ask("Email (opcional)")
            birth = ask("Fecha de nacimiento YYYY-MM-DD (opcional)")
            currency = ask("Moneda", default="USD")
            pid = person_model.create(name, email, birth, currency)
            console.print(f"[good]Persona creada con ID {pid}[/good]")
            _current_person_id = pid
            _current_person_name = name
        elif opt == "3":
            pid = ask_int("ID a editar")
            p = person_model.get(pid)
            if not p:
                console.print("[critical]No encontrado[/critical]"); continue
            name = ask("Nombre", default=p["name"])
            email = ask("Email", default=p["email"] or "")
            birth = ask("Nacimiento", default=p["birth_date"] or "")
            currency = ask("Moneda", default=p["currency"])
            person_model.update(pid, name, email, birth, currency)
            console.print("[good]Actualizado[/good]")
        elif opt == "4":
            pid = ask_int("ID a eliminar")
            if ask_bool("¿Confirmar eliminación? (borra todos sus datos)"):
                person_model.delete(pid)
                if _current_person_id == pid:
                    _current_person_id = None
                    _current_person_name = ""
                console.print("[good]Eliminado[/good]")


# ─────────────────────────────────────────────
# INCOME
# ─────────────────────────────────────────────
def menu_income():
    if not _require_person():
        return
    pid = _current_person_id
    while True:
        console.rule(f"[info]INGRESOS — {_current_person_name}[/info]")
        rows = income_model.list_by_person(pid)
        if rows:
            console.print(tbl.incomes_table(rows))
            gross = income_model.total_gross_monthly(pid)
            net = income_model.total_net_monthly(pid)
            console.print(f"  Total bruto: [money]${gross:,.2f}[/money]/mes  |  Total neto: [money]${net:,.2f}[/money]/mes\n")
        console.print("[1] Agregar  [2] Editar  [3] Eliminar  [0] Volver")
        opt = Prompt.ask("Opción", choices=["1", "2", "3", "0"], default="0")
        if opt == "0":
            break
        elif opt == "1":
            label = ask("Descripción (ej: Salario empresa X)")
            category = ask_choice("Categoría", income_model.CATEGORIES)
            amount = ask_float("Monto mensual bruto $")
            taxable = ask_bool("¿Es gravable?")
            tax_rate = ask_percent("Tasa impositiva efectiva") if taxable else 0.0
            notes = ask("Notas (opcional)")
            income_model.create(pid, label, category, amount, taxable, tax_rate, notes)
            console.print("[good]Ingreso agregado[/good]")
        elif opt == "2":
            iid = ask_int("ID a editar")
            row = income_model.get(iid)
            if not row:
                console.print("[critical]No encontrado[/critical]"); continue
            label = ask("Descripción", default=row["label"])
            category = ask_choice("Categoría", income_model.CATEGORIES, default=row["category"])
            amount = ask_float("Monto mensual $", default=row["amount_monthly"])
            taxable = ask_bool("¿Es gravable?", default=bool(row["is_taxable"]))
            tax_rate = ask_percent("Tasa impositiva", default=row["tax_rate"]) if taxable else 0.0
            notes = ask("Notas", default=row["notes"] or "")
            income_model.update(iid, label, category, amount, taxable, tax_rate, notes)
            console.print("[good]Actualizado[/good]")
        elif opt == "3":
            iid = ask_int("ID a eliminar")
            if ask_bool("¿Confirmar?"):
                income_model.delete(iid)
                console.print("[good]Eliminado[/good]")


# ─────────────────────────────────────────────
# EXPENSES
# ─────────────────────────────────────────────
def menu_expenses():
    if not _require_person():
        return
    pid = _current_person_id
    while True:
        console.rule(f"[info]GASTOS — {_current_person_name}[/info]")
        rows = expense_model.list_by_person(pid)
        if rows:
            console.print(tbl.expenses_table(rows))
            total = expense_model.total_monthly(pid)
            lean = expense_model.total_lean_monthly(pid)
            console.print(f"  Total actual: [debt]${total:,.2f}[/debt]/mes  |  Presupuesto lean: [money]${lean:,.2f}[/money]/mes  |  Ahorro potencial: [money]${total-lean:,.2f}[/money]/mes\n")
        console.print("[1] Agregar  [2] Editar  [3] Eliminar  [4] Simular Presupuesto Lean  [0] Volver")
        opt = Prompt.ask("Opción", choices=["1", "2", "3", "4", "0"], default="0")
        if opt == "0":
            break
        elif opt == "1":
            label = ask("Descripción")
            category = ask_choice("Categoría", expense_model.CATEGORIES)
            etype = ask_choice("Tipo", expense_model.TYPES)
            amount = ask_float("Monto mensual $")
            has_min = ask_bool("¿Tienes un mínimo realista definido?")
            lean_min = ask_float("Mínimo realista $") if has_min else None
            essential = ask_bool("¿Es esencial?")
            notes = ask("Notas (opcional)")
            expense_model.create(pid, label, category, etype, amount, lean_min, essential, notes)
            console.print("[good]Gasto agregado[/good]")
        elif opt == "2":
            eid = ask_int("ID a editar")
            row = expense_model.get(eid)
            if not row:
                console.print("[critical]No encontrado[/critical]"); continue
            label = ask("Descripción", default=row["label"])
            category = ask_choice("Categoría", expense_model.CATEGORIES, default=row["category"])
            etype = ask_choice("Tipo", expense_model.TYPES, default=row["expense_type"])
            amount = ask_float("Monto mensual $", default=row["amount_monthly"])
            has_min = ask_bool("¿Definir mínimo lean?", default=row["realistic_minimum"] is not None)
            lean_min = ask_float("Mínimo realista $", default=row["realistic_minimum"] or 0) if has_min else None
            essential = ask_bool("¿Esencial?", default=bool(row["is_essential"]))
            notes = ask("Notas", default=row["notes"] or "")
            expense_model.update(eid, label, category, etype, amount, lean_min, essential, notes)
            console.print("[good]Actualizado[/good]")
        elif opt == "3":
            eid = ask_int("ID a eliminar")
            if ask_bool("¿Confirmar?"):
                expense_model.delete(eid)
                console.print("[good]Eliminado[/good]")
        elif opt == "4":
            _lean_budget_sim(pid)


def _lean_budget_sim(person_id: int):
    rows = expense_model.list_by_person(person_id)
    total_actual = sum(r["amount_monthly"] for r in rows)
    total_lean = expense_model.total_lean_monthly(person_id)
    saving = total_actual - total_lean
    console.print(Panel(
        f"  Gastos actuales:    [red]${total_actual:,.2f}[/red]/mes\n"
        f"  Presupuesto lean:   [green]${total_lean:,.2f}[/green]/mes\n"
        f"  Ahorro mensual:     [bold green]${saving:,.2f}[/bold green]\n"
        f"  Ahorro anual:       [bold green]${saving*12:,.2f}[/bold green]",
        title="[bold]SIMULACIÓN PRESUPUESTO LEAN[/bold]",
    ))
    input("\nPresiona Enter para continuar...")


# ─────────────────────────────────────────────
# DEBTS
# ─────────────────────────────────────────────
def menu_debts():
    if not _require_person():
        return
    pid = _current_person_id
    while True:
        console.rule(f"[info]DEUDAS — {_current_person_name}[/info]")
        rows = debt_model.list_by_person(pid)
        if rows:
            console.print(tbl.debts_table(rows))
            total_bal = debt_model.total_balance(pid)
            total_pay = debt_model.total_minimum_payments(pid)
            console.print(f"  Balance total: [debt]${total_bal:,.2f}[/debt]  |  Pagos mín.: [debt]${total_pay:,.2f}[/debt]/mes\n")
        console.print("[1] Agregar  [2] Editar  [3] Eliminar  [4] Payoff Avalanche  [5] Payoff Snowball  [0] Volver")
        opt = Prompt.ask("Opción", choices=["1", "2", "3", "4", "5", "0"], default="0")
        if opt == "0":
            break
        elif opt == "1":
            label = ask("Descripción")
            dtype = ask_choice("Tipo de deuda", debt_model.TYPES)
            nature = ask_choice("Naturaleza", debt_model.NATURES)
            balance = ask_float("Balance actual $")
            apr = ask_percent("Tasa interés anual (APR)")
            min_pay = ask_float("Pago mínimo mensual $")
            income_gen = ask_float("¿Ingreso mensual que genera esta deuda? $", default=0.0)
            notes = ask("Notas (opcional)")
            debt_model.create(pid, label, dtype, nature, balance, apr, min_pay,
                              income_generated=income_gen, notes=notes)
            console.print("[good]Deuda agregada[/good]")
        elif opt == "2":
            did = ask_int("ID a editar")
            row = debt_model.get(did)
            if not row:
                console.print("[critical]No encontrado[/critical]"); continue
            label = ask("Descripción", default=row["label"])
            dtype = ask_choice("Tipo", debt_model.TYPES, default=row["debt_type"])
            nature = ask_choice("Naturaleza", debt_model.NATURES, default=row["debt_nature"])
            balance = ask_float("Balance $", default=row["principal_balance"])
            apr = ask_percent("APR", default=row["interest_rate_annual"])
            min_pay = ask_float("Pago mínimo $", default=row["minimum_payment"])
            income_gen = ask_float("Ingreso generado $", default=row["income_generated"])
            maturity = ask("Vencimiento YYYY-MM-DD (opcional)", default=row["maturity_date"] or "")
            notes = ask("Notas", default=row["notes"] or "")
            debt_model.update(did, label, dtype, nature, balance, apr, min_pay, income_gen, maturity or None, notes)
            console.print("[good]Actualizado[/good]")
        elif opt == "3":
            did = ask_int("ID a eliminar")
            if ask_bool("¿Confirmar?"):
                debt_model.delete(did)
                console.print("[good]Eliminado[/good]")
        elif opt in ("4", "5"):
            extra = ask_float("¿Cuánto extra puedes pagar mensualmente? $", default=0.0)
            if opt == "4":
                schedule = payoff.avalanche_schedule(rows, extra)
                console.print(tbl.payoff_table(schedule, "Avalanche (mayor APR primero)"))
            else:
                schedule = payoff.snowball_schedule(rows, extra)
                console.print(tbl.payoff_table(schedule, "Snowball (menor balance primero)"))
            input("\nPresiona Enter para continuar...")


# ─────────────────────────────────────────────
# CREDIT CARDS
# ─────────────────────────────────────────────
def menu_credit_cards():
    if not _require_person():
        return
    pid = _current_person_id
    while True:
        console.rule(f"[info]TARJETAS DE CRÉDITO — {_current_person_name}[/info]")
        rows = cc_model.list_by_person(pid)
        if rows:
            console.print(tbl.credit_cards_table(rows))
            total_bal = cc_model.total_balance(pid)
            total_lim = cc_model.total_limit(pid)
            overall_util = total_bal / total_lim * 100 if total_lim > 0 else 0
            console.print(f"  Balance total: [debt]${total_bal:,.2f}[/debt]  |  Límite total: ${total_lim:,.2f}  |  Utilización: [{'warning' if overall_util > 30 else 'good'}]{overall_util:.1f}%[/]\n")
        console.print("[1] Agregar  [2] Editar  [3] Eliminar  [0] Volver")
        opt = Prompt.ask("Opción", choices=["1", "2", "3", "0"], default="0")
        if opt == "0":
            break
        elif opt == "1":
            card_name = ask("Nombre de la tarjeta")
            issuer = ask("Emisor (banco)")
            limit = ask_float("Límite de crédito $")
            balance = ask_float("Balance actual $")
            apr = ask_percent("APR de la tarjeta")
            min_pay = ask_float("Pago mínimo mensual $")
            due_day = ask_int("Día de corte (1-31)", default=0) or None
            rewards = ask_choice("Tipo de recompensas", cc_model.REWARDS, default="none")
            cc_model.create(pid, card_name, issuer, limit, balance, apr, min_pay, due_day, rewards)
            console.print("[good]Tarjeta agregada[/good]")
        elif opt == "2":
            cid = ask_int("ID a editar")
            row = cc_model.get(cid)
            if not row:
                console.print("[critical]No encontrado[/critical]"); continue
            card_name = ask("Nombre", default=row["card_name"])
            issuer = ask("Emisor", default=row["issuer"] or "")
            limit = ask_float("Límite $", default=row["credit_limit"])
            balance = ask_float("Balance $", default=row["current_balance"])
            apr = ask_percent("APR", default=row["interest_rate"])
            min_pay = ask_float("Pago mínimo $", default=row["min_payment"])
            due_day = ask_int("Día de corte", default=row["due_date_day"] or 0) or None
            rewards = ask_choice("Recompensas", cc_model.REWARDS, default=row["rewards_type"])
            cc_model.update(cid, card_name, issuer, limit, balance, apr, min_pay, due_day, rewards)
            console.print("[good]Actualizado[/good]")
        elif opt == "3":
            cid = ask_int("ID a eliminar")
            if ask_bool("¿Confirmar?"):
                cc_model.delete(cid)
                console.print("[good]Eliminada[/good]")


# ─────────────────────────────────────────────
# INVESTMENTS
# ─────────────────────────────────────────────
def menu_investments():
    if not _require_person():
        return
    pid = _current_person_id
    while True:
        console.rule(f"[info]INVERSIONES — {_current_person_name}[/info]")
        rows = inv_model.list_by_person(pid)
        if rows:
            console.print(tbl.investments_table(rows))
            total = inv_model.total_value(pid)
            income = inv_model.total_income_monthly(pid)
            console.print(f"  Portfolio total: [money]${total:,.2f}[/money]  |  Ingreso mensual: [money]${income:,.2f}[/money]/mes\n")
        console.print("[1] Agregar  [2] Editar  [3] Eliminar  [4] Proyección Valor Futuro  [0] Volver")
        opt = Prompt.ask("Opción", choices=["1", "2", "3", "4", "0"], default="0")
        if opt == "0":
            break
        elif opt == "1":
            label = ask("Descripción")
            cls = ask_choice("Clase de activo", inv_model.CLASSES)
            value = ask_float("Valor actual $")
            basis = ask_float("Costo base $", default=value)
            contrib = ask_float("Contribución mensual $", default=0.0)
            ret = ask_percent("Retorno anual esperado", default=0.07)
            income_mo = ask_float("Ingreso mensual que genera $", default=0.0)
            tax_adv = ask_bool("¿Es cuenta con ventaja fiscal?", default=False)
            acct = ask_choice("Tipo de cuenta", inv_model.ACCOUNTS + ["none"], default="other") if tax_adv else None
            notes = ask("Notas (opcional)")
            inv_model.create(pid, label, cls, value, basis, contrib, ret, income_mo, tax_adv, acct, notes)
            console.print("[good]Inversión agregada[/good]")
        elif opt == "2":
            iid = ask_int("ID a editar")
            row = inv_model.get(iid)
            if not row:
                console.print("[critical]No encontrado[/critical]"); continue
            label = ask("Descripción", default=row["label"])
            cls = ask_choice("Clase", inv_model.CLASSES, default=row["asset_class"])
            value = ask_float("Valor actual $", default=row["current_value"])
            basis = ask_float("Costo base $", default=row["cost_basis"] or value)
            contrib = ask_float("Contribución mensual $", default=row["monthly_contribution"])
            ret = ask_percent("Retorno anual esperado", default=row["expected_annual_return"])
            income_mo = ask_float("Ingreso mensual $", default=row["income_monthly"])
            tax_adv = ask_bool("¿Cuenta con ventaja fiscal?", default=bool(row["is_tax_advantaged"]))
            acct = ask("Tipo de cuenta", default=row["account_type"] or "") if tax_adv else None
            notes = ask("Notas", default=row["notes"] or "")
            inv_model.update(iid, label, cls, value, basis, contrib, ret, income_mo, tax_adv, acct, notes)
            console.print("[good]Actualizado[/good]")
        elif opt == "3":
            iid = ask_int("ID a eliminar")
            if ask_bool("¿Confirmar?"):
                inv_model.delete(iid)
                console.print("[good]Eliminada[/good]")
        elif opt == "4":
            _investment_projector(pid)


def _investment_projector(person_id: int):
    total = inv_model.total_value(person_id)
    contrib = inv_model.total_monthly_contribution(person_id)
    rate = ask_percent("Tasa de retorno anual esperada (total portfolio)", default=0.07)
    rows = ig.projection_table(total, rate, contrib)
    console.print(tbl.projection_table_render(rows, total))
    input("\nPresiona Enter para continuar...")


# ─────────────────────────────────────────────
# ASSETS
# ─────────────────────────────────────────────
def menu_assets():
    if not _require_person():
        return
    pid = _current_person_id
    while True:
        console.rule(f"[info]ACTIVOS FÍSICOS — {_current_person_name}[/info]")
        rows = asset_model.list_by_person(pid)
        if rows:
            console.print(tbl.assets_table(rows))
            console.print(f"  Total activos físicos: [money]${asset_model.total_value(pid):,.2f}[/money]\n")

        nw_data = nw.summary(pid)
        console.print(
            f"  [bold]PATRIMONIO NETO[/bold]: [{'money' if nw_data['net_worth'] >= 0 else 'debt'}]${nw_data['net_worth']:,.2f}[/]\n"
            f"  Activos totales: [money]${nw_data['total_assets']:,.2f}[/money]   "
            f"Pasivos totales: [debt]${nw_data['total_liabilities']:,.2f}[/debt]\n"
        )
        console.print("[1] Agregar  [2] Editar  [3] Eliminar  [0] Volver")
        opt = Prompt.ask("Opción", choices=["1", "2", "3", "0"], default="0")
        if opt == "0":
            break
        elif opt == "1":
            label = ask("Descripción")
            atype = ask_choice("Tipo", asset_model.TYPES)
            value = ask_float("Valor actual $")
            purchase = ask_float("Precio de compra $", default=value)
            purchase_date = ask("Fecha de compra YYYY-MM-DD (opcional)")
            depr = ask_bool("¿Deprecia con el tiempo?", default=False)
            notes = ask("Notas (opcional)")
            asset_model.create(pid, label, atype, value, purchase, purchase_date or None, depr, notes)
            console.print("[good]Activo agregado[/good]")
        elif opt == "2":
            aid = ask_int("ID a editar")
            row = asset_model.get(aid)
            if not row:
                console.print("[critical]No encontrado[/critical]"); continue
            label = ask("Descripción", default=row["label"])
            atype = ask_choice("Tipo", asset_model.TYPES, default=row["asset_type"])
            value = ask_float("Valor actual $", default=row["current_value"])
            purchase = ask_float("Precio de compra $", default=row["purchase_price"] or value)
            purchase_date = ask("Fecha de compra", default=row["purchase_date"] or "")
            depr = ask_bool("¿Deprecia?", default=bool(row["depreciates"]))
            notes = ask("Notas", default=row["notes"] or "")
            asset_model.update(aid, label, atype, value, purchase, purchase_date or None, depr, notes)
            console.print("[good]Actualizado[/good]")
        elif opt == "3":
            aid = ask_int("ID a eliminar")
            if ask_bool("¿Confirmar?"):
                asset_model.delete(aid)
                console.print("[good]Eliminado[/good]")


# ─────────────────────────────────────────────
# AI ADVISOR
# ─────────────────────────────────────────────
def menu_ai():
    if not _require_person():
        return
    pid = _current_person_id
    from ai import advice as adv_module
    from config import ANTHROPIC_API_KEY

    if not ANTHROPIC_API_KEY:
        console.print("[warning]ANTHROPIC_API_KEY no configurado. Agrega tu clave en .env[/warning]")
        input("Presiona Enter para continuar...")
        return

    while True:
        console.rule(f"[info]ASESOR AI — {_current_person_name}[/info]")
        console.print(
            "[1] Análisis financiero completo\n"
            "[2] Plan de eliminación de deuda\n"
            "[3] Optimización de gastos\n"
            "[4] Estrategia de inversión\n"
            "[5] Maximización de ingresos\n"
            "[6] Ver historial de consejos\n"
            "[0] Volver"
        )
        opt = Prompt.ask("Opción", choices=["1", "2", "3", "4", "5", "6", "0"], default="0")
        if opt == "0":
            break
        elif opt == "6":
            _show_advice_history(pid, adv_module)
        else:
            mode_map = {"1": "full", "2": "debt", "3": "expenses", "4": "investment", "5": "income"}
            mode = mode_map[opt]
            console.print(f"[info]Consultando a Claude... (puede tardar unos segundos)[/info]")
            try:
                text, usage = adv_module.get_advice(pid, mode)
                console.print(Panel(
                    Markdown(text),
                    title="[bold cyan]CONSEJO AI[/bold cyan]",
                    border_style="cyan",
                ))
                console.print(f"[muted]Tokens usados: {usage['total_tokens']} (cache read: {usage['cache_read']})[/muted]")
            except Exception as e:
                console.print(f"[critical]Error al consultar AI: {e}[/critical]")
            input("\nPresiona Enter para continuar...")


def _show_advice_history(person_id: int, adv_module):
    history = adv_module.list_advice_history(person_id)
    if not history:
        console.print("[muted]Sin historial aún.[/muted]")
        input("Presiona Enter..."); return
    from ui import tables as tbl
    t = __import__("rich.table", fromlist=["Table"]).Table(title="Historial de Consejos AI")
    t.add_column("ID"); t.add_column("Modo"); t.add_column("Tokens"); t.add_column("Fecha")
    for h in history:
        t.add_row(str(h["id"]), h["advice_mode"], str(h["tokens_used"] or "-"), h["created_at"])
    console.print(t)
    vid = ask_int("ID para ver (0=cancelar)", default=0)
    if vid > 0:
        record = adv_module.get_advice_by_id(vid)
        if record:
            console.print(Panel(Markdown(record["advice_text"]), title="Consejo guardado", border_style="cyan"))
    input("Presiona Enter para continuar...")

#!/usr/bin/env python3
"""
Calculadora financiera CLI para el skill /finanzas.

Subcomandos:
  payoff    -- meses para pagar una deuda y total de intereses
  fv        -- valor futuro de una inversión
  pv        -- valor presente
  fi        -- tiempo hasta independencia financiera (regla del 4%)
  scorecard -- ratios financieros desde un perfil.md
"""

import argparse
import math
import sys
import re
from pathlib import Path
from datetime import date, timedelta


# ── Fórmulas ────────────────────────────────────────────────

def months_to_payoff(balance: float, apr: float, monthly_payment: float) -> int:
    if balance <= 0:
        return 0
    r = apr / 100 / 12
    if r == 0:
        return math.ceil(balance / monthly_payment) if monthly_payment > 0 else 9999
    if monthly_payment <= balance * r:
        return 9999
    return math.ceil(-math.log(1 - (balance * r) / monthly_payment) / math.log(1 + r))


def future_value(pv: float, annual_rate_pct: float, years: int, monthly_contrib: float = 0) -> float:
    r = annual_rate_pct / 100 / 12
    n = years * 12
    fv_lump = pv * (1 + r) ** n
    fv_annuity = monthly_contrib * (((1 + r) ** n - 1) / r) if r > 0 else monthly_contrib * n
    return fv_lump + fv_annuity


def present_value(fv: float, annual_rate_pct: float, years: int) -> float:
    r = annual_rate_pct / 100 / 12
    n = years * 12
    return fv / (1 + r) ** n


def time_to_fi(annual_expenses: float, portfolio: float, annual_contrib: float,
               return_pct: float = 7.0, swr: float = 4.0) -> int:
    fi_target = annual_expenses / (swr / 100)
    if portfolio >= fi_target:
        return 0
    pv = portfolio
    for year in range(1, 101):
        pv = pv * (1 + return_pct / 100) + annual_contrib
        if pv >= fi_target:
            return year
    return 100


# ── Subcomandos ─────────────────────────────────────────────

def cmd_payoff(args):
    total_payment = args.payment + (args.extra or 0)
    months = months_to_payoff(args.balance, args.apr, total_payment)
    total_paid = total_payment * months
    total_interest = total_paid - args.balance
    payoff_date = date.today() + timedelta(days=months * 30)

    print(f"\n📊 PAYOFF CALCULADO")
    print(f"  Deuda inicial:       ${args.balance:,.2f}")
    print(f"  APR:                 {args.apr:.1f}%")
    print(f"  Pago mensual:        ${total_payment:,.2f}/mes")
    if args.extra:
        print(f"  (incluye ${args.extra:,.2f} extra)")
    print()
    if months >= 9999:
        print("  ⚠️  El pago mínimo no cubre los intereses. La deuda crece infinitamente.")
        print(f"  Necesitas pagar más de ${args.balance * args.apr/100/12:,.2f}/mes solo en intereses.")
        return

    print(f"  Meses para pagar:    {months} meses")
    print(f"  Fecha estimada:      {payoff_date.strftime('%B %Y')}")
    print(f"  Total pagado:        ${total_paid:,.2f}")
    print(f"  Total en intereses:  ${total_interest:,.2f}")

    if args.extra:
        months_base = months_to_payoff(args.balance, args.apr, args.payment)
        interest_base = args.payment * months_base - args.balance
        months_saved = months_base - months
        interest_saved = interest_base - total_interest
        print(f"\n  💡 Vs. solo pago mínimo (${args.payment:,.2f}/mes):")
        print(f"     {months_saved} meses menos ({months_base} → {months})")
        print(f"     ${interest_saved:,.2f} menos en intereses")


def cmd_fv(args):
    fv = future_value(args.pv, args.rate, args.years, args.contribution or 0)
    gain = fv - args.pv - (args.contribution or 0) * args.years * 12
    total_contrib = (args.contribution or 0) * args.years * 12

    print(f"\n📈 VALOR FUTURO")
    print(f"  Capital inicial:     ${args.pv:,.2f}")
    print(f"  Contribución/mes:    ${args.contribution or 0:,.2f}")
    print(f"  Tasa anual:          {args.rate:.1f}%")
    print(f"  Horizonte:           {args.years} años")
    print()
    print(f"  Valor futuro:        ${fv:,.2f}")
    print(f"  Total aportado:      ${args.pv + total_contrib:,.2f}")
    print(f"  Ganancia por retorno: ${gain:,.2f}")
    print(f"  Múltiplo:            {fv / args.pv:.1f}x")

    horizons = [1, 5, 10, 20, 30]
    print(f"\n  Proyección:")
    for y in horizons:
        if y <= args.years:
            v = future_value(args.pv, args.rate, y, args.contribution or 0)
            print(f"    {y:2d} años: ${v:>14,.0f}")


def cmd_pv(args):
    pv = present_value(args.fv, args.rate, args.years)
    print(f"\n💰 VALOR PRESENTE")
    print(f"  Valor futuro deseado: ${args.fv:,.2f}")
    print(f"  Tasa anual:           {args.rate:.1f}%")
    print(f"  En:                   {args.years} años")
    print()
    print(f"  Debes invertir hoy:   ${pv:,.2f}")
    print(f"  Poder adquisitivo:    ${pv / args.fv * 100:.1f}% del valor futuro en dinero de hoy")


def cmd_fi(args):
    fi_target = args.expenses / (args.swr / 100)
    years = time_to_fi(args.expenses, args.portfolio, args.contribution * 12, args.rate, args.swr)
    fi_date = date.today().year + years
    current_progress = args.portfolio / fi_target * 100

    print(f"\n🎯 INDEPENDENCIA FINANCIERA")
    print(f"  Gastos anuales:      ${args.expenses:,.2f}")
    print(f"  Tasa retiro seguro:  {args.swr:.1f}% (regla del {args.swr:.0f}%)")
    print(f"  Meta FI (portafolio): ${fi_target:,.2f}")
    print()
    print(f"  Portafolio actual:   ${args.portfolio:,.2f} ({current_progress:.1f}% del camino)")
    print(f"  Contribución/mes:    ${args.contribution:,.2f}")
    print(f"  Retorno esperado:    {args.rate:.1f}% anual")
    print()
    if years == 0:
        print(f"  🎉 ¡Ya alcanzaste la IF! Tu portafolio cubre tus gastos.")
    else:
        print(f"  Años para IF:        {years} años")
        print(f"  Año estimado:        {fi_date}")
        fv_at_fi = future_value(args.portfolio, args.rate, years, args.contribution)
        print(f"  Portafolio en {years} años: ${fv_at_fi:,.2f}")
        monthly_passive = fv_at_fi * (args.swr / 100) / 12
        print(f"  Ingreso pasivo mensual: ${monthly_passive:,.2f}/mes")


def cmd_scorecard(args):
    perfil_path = Path(args.perfil).expanduser()
    if not perfil_path.exists():
        print(f"[ERROR] No se encontró el perfil: {perfil_path}")
        sys.exit(1)

    content = perfil_path.read_text()

    def extract_money(text: str) -> list[float]:
        return [float(v.replace(",", "")) for v in re.findall(r'\$([0-9,]+(?:\.[0-9]+)?)', text)]

    def extract_pct(text: str) -> list[float]:
        return [float(v) for v in re.findall(r'([0-9]+(?:\.[0-9]+)?)\s*%', text)]

    sections = {}
    current = None
    for line in content.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current:
            sections[current].append(line)

    print(f"\n📋 SCORECARD: {perfil_path.parent.name}")
    print(f"  Perfil: {perfil_path}")
    print()

    # Ingresos
    income_section = "\n".join(sections.get("Ingresos", []))
    income_amounts = extract_money(income_section)
    total_income = sum(income_amounts[::3]) if income_amounts else 0  # cada 3 cols: bruto, impuesto, neto

    # Gastos
    expense_section = "\n".join(sections.get("Gastos", []))
    expense_amounts = extract_money(expense_section)
    total_expenses = sum(expense_amounts[::2]) if expense_amounts else 0

    # Deudas
    debt_section = "\n".join(sections.get("Deudas", []))
    debt_amounts = extract_money(debt_section)

    # Inversiones
    inv_section = "\n".join(sections.get("Inversiones", []))
    inv_amounts = extract_money(inv_section)
    total_portfolio = sum(inv_amounts[::4]) if inv_amounts else 0  # columna valor actual

    print(f"  Ingreso bruto estimado:  ${total_income:,.0f}/mes")
    print(f"  Gastos totales:          ${total_expenses:,.0f}/mes")
    print(f"  Portafolio total:        ${total_portfolio:,.0f}")
    print()
    print("  ⚠️  Para un scorecard completo, proporciona los valores directamente en el chat.")
    print("  Claude puede leer el perfil.md y calcular DTI, utilización, ratio IF y más.")


# ── Main ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Calculadora financiera para /finanzas skill")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # payoff
    p = sub.add_parser("payoff", help="Meses para pagar una deuda")
    p.add_argument("--balance", type=float, required=True)
    p.add_argument("--apr", type=float, required=True, help="APR en porcentaje (ej: 18.5)")
    p.add_argument("--payment", type=float, required=True, help="Pago mensual base")
    p.add_argument("--extra", type=float, default=0, help="Pago extra mensual")

    # fv
    p = sub.add_parser("fv", help="Valor futuro")
    p.add_argument("--pv", type=float, required=True, help="Valor presente / capital inicial")
    p.add_argument("--rate", type=float, required=True, help="Tasa anual en % (ej: 7)")
    p.add_argument("--years", type=int, required=True)
    p.add_argument("--contribution", type=float, default=0, help="Contribución mensual")

    # pv
    p = sub.add_parser("pv", help="Valor presente")
    p.add_argument("--fv", type=float, required=True)
    p.add_argument("--rate", type=float, required=True)
    p.add_argument("--years", type=int, required=True)

    # fi
    p = sub.add_parser("fi", help="Tiempo hasta independencia financiera")
    p.add_argument("--expenses", type=float, required=True, help="Gastos anuales")
    p.add_argument("--portfolio", type=float, required=True, help="Portafolio actual")
    p.add_argument("--contribution", type=float, required=True, help="Contribución mensual")
    p.add_argument("--rate", type=float, default=7.0, help="Retorno anual esperado %")
    p.add_argument("--swr", type=float, default=4.0, help="Tasa de retiro seguro %")

    # scorecard
    p = sub.add_parser("scorecard", help="Ratios desde perfil.md")
    p.add_argument("--perfil", required=True, help="Ruta al perfil.md")

    args = parser.parse_args()

    dispatch = {
        "payoff": cmd_payoff,
        "fv": cmd_fv,
        "pv": cmd_pv,
        "fi": cmd_fi,
        "scorecard": cmd_scorecard,
    }
    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()

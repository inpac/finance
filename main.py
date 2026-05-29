#!/usr/bin/env python3
import sys
from rich.prompt import Prompt
from rich.panel import Panel

from db.schema import init_db
from ui.console import console
from ui import menus
from ui.dashboard import show_dashboard
from config import DEBUG

if DEBUG:
    from rich.traceback import install
    install(show_locals=True)


BANNER = """[bold cyan]
 ███████╗██╗███╗   ██╗ █████╗ ███╗   ██╗███████╗███████╗
 ██╔════╝██║████╗  ██║██╔══██╗████╗  ██║██╔════╝██╔════╝
 █████╗  ██║██╔██╗ ██║███████║██╔██╗ ██║███████╗█████╗
 ██╔══╝  ██║██║╚██╗██║██╔══██║██║╚██╗██║╚════██║██╔══╝
 ██║     ██║██║ ╚████║██║  ██║██║ ╚████║███████║███████╗
 ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝
[/bold cyan]
[bold]Sistema de Gestión Financiera Personal[/bold]
[muted]Maximiza ingresos • Minimiza gastos • Elimina deuda de consumo • Alcanza la IF[/muted]
"""


def main_menu():
    init_db()
    console.print(BANNER)

    while True:
        person_name = menus._current_person_name or "[sin seleccionar]"
        person_display = f"[cyan]{person_name}[/cyan]" if menus._current_person_id else "[warning]sin seleccionar[/warning]"

        console.rule(f"[bold]MENÚ PRINCIPAL[/bold] — Persona activa: {person_display}")
        console.print(
            "\n"
            "  [1] 👤 Personas\n"
            "  [2] 💰 Ingresos\n"
            "  [3] 💸 Gastos\n"
            "  [4] 🏦 Deudas\n"
            "  [5] 💳 Tarjetas de Crédito\n"
            "  [6] 📈 Inversiones\n"
            "  [7] 🏠 Activos & Patrimonio Neto\n"
            "  [8] 📊 Dashboard Completo\n"
            "  [9] 🤖 Asesor AI (Claude)\n"
            "  [0] Salir\n"
        )

        opt = Prompt.ask("Elige una opción", choices=["0","1","2","3","4","5","6","7","8","9"])

        if opt == "0":
            console.print("[info]¡Hasta luego! Recuerda: la IF es el destino.[/info]")
            break
        elif opt == "1":
            menus.menu_persons()
        elif opt == "2":
            menus.menu_income()
        elif opt == "3":
            menus.menu_expenses()
        elif opt == "4":
            menus.menu_debts()
        elif opt == "5":
            menus.menu_credit_cards()
        elif opt == "6":
            menus.menu_investments()
        elif opt == "7":
            menus.menu_assets()
        elif opt == "8":
            if menus._current_person_id:
                show_dashboard(menus._current_person_id)
                input("\nPresiona Enter para continuar...")
            else:
                console.print("[warning]Selecciona una persona primero (opción 1)[/warning]")
        elif opt == "9":
            menus.menu_ai()


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[muted]Saliendo...[/muted]")
        sys.exit(0)

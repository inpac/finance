"""Datos demo para probar el sistema. Ejecutar: python db/seed.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db.schema import init_db
import models.person as pm
import models.income as im
import models.expense as em
import models.debt as dm
import models.credit_card as ccm
import models.investment as invm
import models.asset as am


def seed():
    init_db()

    pid = pm.create("Ana García", "ana@ejemplo.com", "1990-03-15", "USD")
    print(f"Persona creada: ID {pid}")

    im.create(pid, "Salario empresa Tech", "salary", 5500, True, 0.22)
    im.create(pid, "Freelance diseño", "variable", 800, True, 0.15)
    im.create(pid, "Dividendos ETF", "passive", 120, True, 0.15)

    em.create(pid, "Renta apartamento", "housing", "fixed", 1400, 1200, True)
    em.create(pid, "Supermercado", "food", "variable", 450, 320, True)
    em.create(pid, "Transporte / gasolina", "transport", "variable", 280, 200, True)
    em.create(pid, "Seguro médico", "health", "fixed", 200, 200, True)
    em.create(pid, "Netflix + Spotify + Disney", "entertainment", "fixed", 55, 15, False, "Cancelar 2 de 3")
    em.create(pid, "Restaurantes / salidas", "food", "variable", 380, 180, False)
    em.create(pid, "Ropa / compras", "other", "variable", 200, 80, False)
    em.create(pid, "Servicios (luz, agua, internet)", "utilities", "fixed", 180, 150, True)

    dm.create(pid, "Hipoteca depto alquiler", "mortgage", "income_generating",
              180000, 0.065, 950, income_generated=1400, notes="Genera ingreso de renta")
    dm.create(pid, "Préstamo auto", "auto", "consumption", 14500, 0.089, 320)
    dm.create(pid, "Préstamo personal banco", "personal_loan", "consumption", 8200, 0.185, 280)

    ccm.create(pid, "Visa Platinum", "Banco Nacional", 10000, 4800, 0.22, 144, 15, "cashback")
    ccm.create(pid, "Amex Gold", "American Express", 15000, 1200, 0.18, 36, 28, "points")

    invm.create(pid, "S&P 500 Index Fund", "etf", 28000, 20000, 500, 0.10, 0, True, "401k")
    invm.create(pid, "Acciones tech (AAPL, MSFT)", "stock", 12000, 9500, 200, 0.12, 60, False, "taxable")
    invm.create(pid, "Renta depto alquiler (equity)", "real_estate", 45000, 40000, 0, 0.06, 450, False, "taxable")

    am.create(pid, "Auto Honda 2021", "vehicle", 18000, 22000, "2021-06-01", True)
    am.create(pid, "Muebles y equipo hogar", "other", 5000, 8000, "2020-01-01", True)

    print("✓ Datos demo creados para Ana García")
    print(f"  Corre: python main.py  — selecciona persona ID {pid}")


if __name__ == "__main__":
    seed()

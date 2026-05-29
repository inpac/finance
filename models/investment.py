from db.connection import get_connection

CLASSES = ["stock", "bond", "real_estate", "fund", "etf", "crypto", "cash", "business", "other"]
ACCOUNTS = ["401k", "IRA", "Roth_IRA", "taxable", "TFSA", "RRSP", "pension", "other"]


def create(person_id, label, asset_class, current_value, cost_basis=None,
           monthly_contribution=0.0, expected_annual_return=0.07, income_monthly=0.0,
           is_tax_advantaged=False, account_type=None, notes="") -> int:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO investments (person_id, label, asset_class, current_value, cost_basis,
           monthly_contribution, expected_annual_return, income_monthly, is_tax_advantaged,
           account_type, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (person_id, label, asset_class, current_value, cost_basis or current_value,
         monthly_contribution, expected_annual_return, income_monthly,
         int(is_tax_advantaged), account_type, notes or None),
    )
    conn.commit()
    return cur.lastrowid


def list_by_person(person_id) -> list:
    return get_connection().execute(
        "SELECT * FROM investments WHERE person_id=? ORDER BY current_value DESC",
        (person_id,),
    ).fetchall()


def get(inv_id: int):
    return get_connection().execute("SELECT * FROM investments WHERE id=?", (inv_id,)).fetchone()


def update(inv_id, label, asset_class, current_value, cost_basis, monthly_contribution,
           expected_annual_return, income_monthly, is_tax_advantaged, account_type, notes):
    conn = get_connection()
    conn.execute(
        """UPDATE investments SET label=?, asset_class=?, current_value=?, cost_basis=?,
           monthly_contribution=?, expected_annual_return=?, income_monthly=?,
           is_tax_advantaged=?, account_type=?, notes=? WHERE id=?""",
        (label, asset_class, current_value, cost_basis, monthly_contribution,
         expected_annual_return, income_monthly, int(is_tax_advantaged),
         account_type, notes or None, inv_id),
    )
    conn.commit()


def delete(inv_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM investments WHERE id=?", (inv_id,))
    conn.commit()


def total_value(person_id) -> float:
    row = get_connection().execute(
        "SELECT COALESCE(SUM(current_value),0) FROM investments WHERE person_id=?", (person_id,)
    ).fetchone()
    return row[0]


def total_income_monthly(person_id) -> float:
    row = get_connection().execute(
        "SELECT COALESCE(SUM(income_monthly),0) FROM investments WHERE person_id=?", (person_id,)
    ).fetchone()
    return row[0]


def total_monthly_contribution(person_id) -> float:
    row = get_connection().execute(
        "SELECT COALESCE(SUM(monthly_contribution),0) FROM investments WHERE person_id=?", (person_id,)
    ).fetchone()
    return row[0]

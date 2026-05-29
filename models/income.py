from db.connection import get_connection

CATEGORIES = ["salary", "passive", "variable", "business", "rental", "other"]


def create(person_id, label, category, amount_monthly, is_taxable=True, tax_rate=0.0, notes="") -> int:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO incomes (person_id, label, category, amount_monthly, is_taxable, tax_rate, notes)
           VALUES (?,?,?,?,?,?,?)""",
        (person_id, label, category, amount_monthly, int(is_taxable), tax_rate, notes or None),
    )
    conn.commit()
    return cur.lastrowid


def list_by_person(person_id) -> list:
    return get_connection().execute(
        "SELECT * FROM incomes WHERE person_id=? ORDER BY amount_monthly DESC",
        (person_id,),
    ).fetchall()


def get(income_id: int):
    return get_connection().execute("SELECT * FROM incomes WHERE id=?", (income_id,)).fetchone()


def update(income_id, label, category, amount_monthly, is_taxable, tax_rate, notes):
    conn = get_connection()
    conn.execute(
        """UPDATE incomes SET label=?, category=?, amount_monthly=?,
           is_taxable=?, tax_rate=?, notes=? WHERE id=?""",
        (label, category, amount_monthly, int(is_taxable), tax_rate, notes or None, income_id),
    )
    conn.commit()


def delete(income_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM incomes WHERE id=?", (income_id,))
    conn.commit()


def total_gross_monthly(person_id) -> float:
    row = get_connection().execute(
        "SELECT COALESCE(SUM(amount_monthly),0) FROM incomes WHERE person_id=?", (person_id,)
    ).fetchone()
    return row[0]


def total_net_monthly(person_id) -> float:
    rows = list_by_person(person_id)
    return sum(r["amount_monthly"] * (1 - r["tax_rate"]) for r in rows)


def total_passive_monthly(person_id) -> float:
    row = get_connection().execute(
        "SELECT COALESCE(SUM(amount_monthly),0) FROM incomes WHERE person_id=? AND category IN ('passive','rental','business')",
        (person_id,),
    ).fetchone()
    return row[0]

from db.connection import get_connection

CATEGORIES = ["housing", "food", "transport", "health", "education", "entertainment", "utilities", "insurance", "other"]
TYPES = ["fixed", "variable"]


def create(person_id, label, category, expense_type, amount_monthly,
           realistic_minimum=None, is_essential=True, notes="") -> int:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO expenses (person_id, label, category, expense_type, amount_monthly,
           realistic_minimum, is_essential, notes) VALUES (?,?,?,?,?,?,?,?)""",
        (person_id, label, category, expense_type, amount_monthly,
         realistic_minimum, int(is_essential), notes or None),
    )
    conn.commit()
    return cur.lastrowid


def list_by_person(person_id) -> list:
    return get_connection().execute(
        "SELECT * FROM expenses WHERE person_id=? ORDER BY amount_monthly DESC",
        (person_id,),
    ).fetchall()


def get(expense_id: int):
    return get_connection().execute("SELECT * FROM expenses WHERE id=?", (expense_id,)).fetchone()


def update(expense_id, label, category, expense_type, amount_monthly,
           realistic_minimum, is_essential, notes):
    conn = get_connection()
    conn.execute(
        """UPDATE expenses SET label=?, category=?, expense_type=?, amount_monthly=?,
           realistic_minimum=?, is_essential=?, notes=? WHERE id=?""",
        (label, category, expense_type, amount_monthly,
         realistic_minimum, int(is_essential), notes or None, expense_id),
    )
    conn.commit()


def delete(expense_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()


def total_monthly(person_id) -> float:
    row = get_connection().execute(
        "SELECT COALESCE(SUM(amount_monthly),0) FROM expenses WHERE person_id=?", (person_id,)
    ).fetchone()
    return row[0]


def total_lean_monthly(person_id) -> float:
    rows = list_by_person(person_id)
    return sum(
        (r["realistic_minimum"] if r["realistic_minimum"] is not None else r["amount_monthly"])
        for r in rows
    )

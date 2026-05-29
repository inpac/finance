from db.connection import get_connection

TYPES = ["credit_card", "personal_loan", "auto", "mortgage", "student", "business", "other"]
NATURES = ["consumption", "income_generating"]


def create(person_id, label, debt_type, debt_nature, principal_balance,
           interest_rate_annual, minimum_payment, original_principal=None,
           income_generated=0.0, maturity_date=None, notes="") -> int:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO debts (person_id, label, debt_type, debt_nature, principal_balance,
           original_principal, interest_rate_annual, minimum_payment, income_generated,
           maturity_date, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (person_id, label, debt_type, debt_nature, principal_balance,
         original_principal or principal_balance, interest_rate_annual,
         minimum_payment, income_generated, maturity_date, notes or None),
    )
    conn.commit()
    return cur.lastrowid


def list_by_person(person_id) -> list:
    return get_connection().execute(
        "SELECT * FROM debts WHERE person_id=? ORDER BY interest_rate_annual DESC",
        (person_id,),
    ).fetchall()


def get(debt_id: int):
    return get_connection().execute("SELECT * FROM debts WHERE id=?", (debt_id,)).fetchone()


def update(debt_id, label, debt_type, debt_nature, principal_balance,
           interest_rate_annual, minimum_payment, income_generated, maturity_date, notes):
    conn = get_connection()
    conn.execute(
        """UPDATE debts SET label=?, debt_type=?, debt_nature=?, principal_balance=?,
           interest_rate_annual=?, minimum_payment=?, income_generated=?,
           maturity_date=?, notes=? WHERE id=?""",
        (label, debt_type, debt_nature, principal_balance, interest_rate_annual,
         minimum_payment, income_generated, maturity_date, notes or None, debt_id),
    )
    conn.commit()


def delete(debt_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM debts WHERE id=?", (debt_id,))
    conn.commit()


def total_balance(person_id) -> float:
    row = get_connection().execute(
        "SELECT COALESCE(SUM(principal_balance),0) FROM debts WHERE person_id=?", (person_id,)
    ).fetchone()
    return row[0]


def total_minimum_payments(person_id) -> float:
    row = get_connection().execute(
        "SELECT COALESCE(SUM(minimum_payment),0) FROM debts WHERE person_id=?", (person_id,)
    ).fetchone()
    return row[0]


def total_income_generated(person_id) -> float:
    row = get_connection().execute(
        "SELECT COALESCE(SUM(income_generated),0) FROM debts WHERE person_id=?", (person_id,)
    ).fetchone()
    return row[0]

from db.connection import get_connection

REWARDS = ["cashback", "points", "miles", "none"]


def create(person_id, card_name, issuer, credit_limit, current_balance,
           interest_rate, min_payment, due_date_day=None, rewards_type="none") -> int:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO credit_cards (person_id, card_name, issuer, credit_limit, current_balance,
           interest_rate, min_payment, due_date_day, rewards_type)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (person_id, card_name, issuer or None, credit_limit, current_balance,
         interest_rate, min_payment, due_date_day, rewards_type),
    )
    conn.commit()
    return cur.lastrowid


def list_by_person(person_id) -> list:
    return get_connection().execute(
        "SELECT * FROM credit_cards WHERE person_id=? ORDER BY interest_rate DESC",
        (person_id,),
    ).fetchall()


def get(card_id: int):
    return get_connection().execute("SELECT * FROM credit_cards WHERE id=?", (card_id,)).fetchone()


def update(card_id, card_name, issuer, credit_limit, current_balance,
           interest_rate, min_payment, due_date_day, rewards_type):
    conn = get_connection()
    conn.execute(
        """UPDATE credit_cards SET card_name=?, issuer=?, credit_limit=?, current_balance=?,
           interest_rate=?, min_payment=?, due_date_day=?, rewards_type=? WHERE id=?""",
        (card_name, issuer or None, credit_limit, current_balance, interest_rate,
         min_payment, due_date_day, rewards_type, card_id),
    )
    conn.commit()


def delete(card_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM credit_cards WHERE id=?", (card_id,))
    conn.commit()


def total_balance(person_id) -> float:
    row = get_connection().execute(
        "SELECT COALESCE(SUM(current_balance),0) FROM credit_cards WHERE person_id=?", (person_id,)
    ).fetchone()
    return row[0]


def total_limit(person_id) -> float:
    row = get_connection().execute(
        "SELECT COALESCE(SUM(credit_limit),0) FROM credit_cards WHERE person_id=?", (person_id,)
    ).fetchone()
    return row[0]

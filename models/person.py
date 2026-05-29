from db.connection import get_connection


def create(name: str, email: str = "", birth_date: str = "", currency: str = "USD") -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO persons (name, email, birth_date, currency) VALUES (?,?,?,?)",
        (name, email or None, birth_date or None, currency),
    )
    conn.commit()
    return cur.lastrowid


def list_all() -> list:
    return get_connection().execute(
        "SELECT * FROM persons ORDER BY name"
    ).fetchall()


def get(person_id: int):
    return get_connection().execute(
        "SELECT * FROM persons WHERE id=?", (person_id,)
    ).fetchone()


def update(person_id: int, name: str, email: str, birth_date: str, currency: str):
    conn = get_connection()
    conn.execute(
        """UPDATE persons SET name=?, email=?, birth_date=?, currency=?,
           updated_at=CURRENT_TIMESTAMP WHERE id=?""",
        (name, email or None, birth_date or None, currency, person_id),
    )
    conn.commit()


def delete(person_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM persons WHERE id=?", (person_id,))
    conn.commit()

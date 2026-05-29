from db.connection import get_connection

TYPES = ["real_estate", "vehicle", "business", "jewelry", "art", "other"]


def create(person_id, label, asset_type, current_value, purchase_price=None,
           purchase_date=None, depreciates=False, notes="") -> int:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO assets (person_id, label, asset_type, current_value, purchase_price,
           purchase_date, depreciates, notes) VALUES (?,?,?,?,?,?,?,?)""",
        (person_id, label, asset_type, current_value, purchase_price,
         purchase_date, int(depreciates), notes or None),
    )
    conn.commit()
    return cur.lastrowid


def list_by_person(person_id) -> list:
    return get_connection().execute(
        "SELECT * FROM assets WHERE person_id=? ORDER BY current_value DESC",
        (person_id,),
    ).fetchall()


def get(asset_id: int):
    return get_connection().execute("SELECT * FROM assets WHERE id=?", (asset_id,)).fetchone()


def update(asset_id, label, asset_type, current_value, purchase_price,
           purchase_date, depreciates, notes):
    conn = get_connection()
    conn.execute(
        """UPDATE assets SET label=?, asset_type=?, current_value=?, purchase_price=?,
           purchase_date=?, depreciates=?, notes=? WHERE id=?""",
        (label, asset_type, current_value, purchase_price, purchase_date,
         int(depreciates), notes or None, asset_id),
    )
    conn.commit()


def delete(asset_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM assets WHERE id=?", (asset_id,))
    conn.commit()


def total_value(person_id) -> float:
    row = get_connection().execute(
        "SELECT COALESCE(SUM(current_value),0) FROM assets WHERE person_id=?", (person_id,)
    ).fetchone()
    return row[0]

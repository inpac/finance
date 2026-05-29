from db.connection import get_connection

SCHEMA_VERSION = 1

_TABLES = """
CREATE TABLE IF NOT EXISTS schema_meta (
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS persons (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    email       TEXT,
    birth_date  DATE,
    currency    TEXT DEFAULT 'USD',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS incomes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id       INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    label           TEXT NOT NULL,
    category        TEXT NOT NULL,
    amount_monthly  REAL NOT NULL,
    is_taxable      INTEGER DEFAULT 1,
    tax_rate        REAL DEFAULT 0.0,
    notes           TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS expenses (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id           INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    label               TEXT NOT NULL,
    category            TEXT NOT NULL,
    expense_type        TEXT NOT NULL,
    amount_monthly      REAL NOT NULL,
    realistic_minimum   REAL,
    is_essential        INTEGER DEFAULT 1,
    notes               TEXT,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS debts (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id               INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    label                   TEXT NOT NULL,
    debt_type               TEXT NOT NULL,
    debt_nature             TEXT NOT NULL,
    principal_balance       REAL NOT NULL,
    original_principal      REAL,
    interest_rate_annual    REAL NOT NULL,
    minimum_payment         REAL NOT NULL,
    payment_frequency       TEXT DEFAULT 'monthly',
    income_generated        REAL DEFAULT 0.0,
    maturity_date           DATE,
    notes                   TEXT,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS credit_cards (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id       INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    card_name       TEXT NOT NULL,
    issuer          TEXT,
    credit_limit    REAL NOT NULL,
    current_balance REAL NOT NULL,
    interest_rate   REAL NOT NULL,
    min_payment     REAL NOT NULL,
    due_date_day    INTEGER,
    rewards_type    TEXT DEFAULT 'none',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS investments (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id               INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    label                   TEXT NOT NULL,
    asset_class             TEXT NOT NULL,
    current_value           REAL NOT NULL,
    cost_basis              REAL,
    monthly_contribution    REAL DEFAULT 0.0,
    expected_annual_return  REAL DEFAULT 0.07,
    income_monthly          REAL DEFAULT 0.0,
    is_tax_advantaged       INTEGER DEFAULT 0,
    account_type            TEXT,
    notes                   TEXT,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assets (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id       INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    label           TEXT NOT NULL,
    asset_type      TEXT NOT NULL,
    current_value   REAL NOT NULL,
    purchase_price  REAL,
    purchase_date   DATE,
    depreciates     INTEGER DEFAULT 0,
    notes           TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_advice (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id       INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    advice_mode     TEXT NOT NULL,
    prompt_snapshot TEXT NOT NULL,
    advice_text     TEXT NOT NULL,
    tokens_used     INTEGER,
    model           TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_incomes_person     ON incomes(person_id);
CREATE INDEX IF NOT EXISTS idx_expenses_person    ON expenses(person_id);
CREATE INDEX IF NOT EXISTS idx_debts_person       ON debts(person_id);
CREATE INDEX IF NOT EXISTS idx_cc_person          ON credit_cards(person_id);
CREATE INDEX IF NOT EXISTS idx_investments_person ON investments(person_id);
CREATE INDEX IF NOT EXISTS idx_assets_person      ON assets(person_id);
CREATE INDEX IF NOT EXISTS idx_advice_person      ON ai_advice(person_id);
"""


def init_db():
    conn = get_connection()
    conn.executescript(_TABLES)
    row = conn.execute("SELECT version FROM schema_meta").fetchone()
    if row is None:
        conn.execute("INSERT INTO schema_meta VALUES (?)", (SCHEMA_VERSION,))
        conn.commit()

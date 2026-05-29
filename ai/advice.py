from ai.client import call_claude
from ai.prompts import SYSTEM_PROMPT, build_snapshot
from db.connection import get_connection
from config import DEFAULT_MODEL

MODES = {
    "full": "Provide a complete financial independence analysis covering all aspects of the financial profile below.",
    "debt": "Focus EXCLUSIVELY on debt elimination strategy. Rank all debts by urgency, provide the avalanche payoff schedule with exact monthly amounts and payoff dates, and calculate total interest saved.",
    "expenses": "Focus EXCLUSIVELY on expense optimization. Identify every expense that can be reduced to its realistic minimum, calculate total monthly savings, and prioritize cuts by impact.",
    "investment": "Focus EXCLUSIVELY on investment strategy. Analyze portfolio allocation, expected growth, passive income trajectory, and provide specific reallocation recommendations to accelerate FI.",
    "income": "Focus EXCLUSIVELY on income maximization. Identify gaps, suggest 3-5 concrete new income streams suited to this person's profile, and model the FI timeline impact.",
}


def get_advice(person_id: int, mode: str = "full") -> tuple[str, dict]:
    if mode not in MODES:
        mode = "full"
    snapshot = build_snapshot(person_id)
    user_msg = f"{MODES[mode]}\n\n{snapshot}"
    text, usage = call_claude(SYSTEM_PROMPT, user_msg, DEFAULT_MODEL)
    _save(person_id, mode, snapshot, text, usage)
    return text, usage


def _save(person_id: int, mode: str, snapshot: str, text: str, usage: dict):
    conn = get_connection()
    conn.execute(
        """INSERT INTO ai_advice (person_id, advice_mode, prompt_snapshot, advice_text, tokens_used, model)
           VALUES (?,?,?,?,?,?)""",
        (person_id, mode, snapshot, text, usage.get("total_tokens"), DEFAULT_MODEL),
    )
    conn.commit()


def list_advice_history(person_id: int) -> list:
    return get_connection().execute(
        "SELECT id, advice_mode, tokens_used, created_at FROM ai_advice WHERE person_id=? ORDER BY created_at DESC LIMIT 20",
        (person_id,),
    ).fetchall()


def get_advice_by_id(advice_id: int):
    return get_connection().execute(
        "SELECT * FROM ai_advice WHERE id=?", (advice_id,)
    ).fetchone()

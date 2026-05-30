# 💰 financeabc123 — Personal Financial Advisor for Claude Code

A Claude Code skill that acts as your personal financial advisor — grounded in the philosophy of four proven wealth-building books. Upload your bank statements, credit card reports, or just type your numbers, and get real, actionable advice in your language.

No app. No subscription. No API key. Just Claude Code.

---

## What It Does

- **Analyzes your financial files** — CSV, PDF, Excel, images, bank statements, anything
- **Builds a personal financial profile** — stored as a markdown file on your machine, private and versionable
- **Runs financial calculations** — debt payoff timelines, investment projections, financial independence date
- **Gives advice grounded in proven wealth principles** — not generic tips, but frameworks from 4 foundational books
- **Speaks your language** — English, Español, Français, Deutsch, Italiano, Português, 中文, 日本語

---

## The Philosophy

This skill doesn't just crunch numbers. It's built on the core wisdom of four books that together form a complete wealth worldview:

| Book | Core Truth |
|------|-----------|
| 📖 *The Psychology of Money* — Morgan Housel | Behavior beats intelligence. Freedom is the goal. |
| 📖 *The Simple Path to Wealth* — JL Collins | Spend less, invest the surplus, avoid debt, own index funds. |
| 📖 *The Millionaire Next Door* — Stanley & Danko | Wealth is built quietly, below your means, through discipline. |
| 📖 *Family Wealth* — James Hughes Jr. | Money alone isn't enough. Human and intellectual capital matter more. |

### Unlearn → Relearn

| ❌ Common Myth | ✅ Proven Truth |
|----------------|----------------|
| High income = wealth | Wealth is what you *don't* spend |
| Complex investments = better returns | Simple index funds beat 99% of strategies |
| Smart people win at investing | Behavior beats intelligence every time |
| Debt is normal | Debt is a leech on your future freedom |
| Money = happiness | Freedom = the highest dividend money can buy |

---

## How to Install

**1. Clone this repo into your Claude Code skills folder:**

```bash
# Global (works in any Claude Code session)
git clone https://github.com/inpac/finance ~/.claude/skills/financeabc123

# Or project-level (works only in this project)
git clone https://github.com/inpac/finance .claude/skills/financeabc123
```

**2. Install the file parser (optional — needed for uploading files):**

```bash
pip install markitdown
```

That's it. No configuration, no API keys, no database.

---

## How to Use

Open any Claude Code session (web, desktop, or terminal) and type:

```
/financeabc123
```

Claude loads the skill and greets you. From there:

- **Upload files** — drag and drop a bank statement, Excel budget, or PDF
- **Type your numbers** — income, expenses, debts, investments
- **Ask questions** — "when will I be financially free?", "should I pay off debt or invest?", "am I saving enough?"

### Example session

```
You:    /financeabc123
Claude: ¡Bienvenido! ¿Tienes archivos para subir o empezamos desde cero?

You:    [uploads bank_statement_may.csv]
Claude: Encontré 58 transacciones. Resumen:
        - Ingresos netos: $4,800/mes
        - Gastos: $4,210/mes
        - Flujo: +$590/mes (tasa de ahorro: 12.3%)

        Con esta tasa, tu independencia financiera es en ~28 años.
        The Millionaire Next Door promedia 20%+ de ahorro.
        ¿Revisamos qué gastos tienen un "lean floor" más bajo?

You:    Tengo una tarjeta al 22% APR con $3,400 de balance
Claude: Emergencia financiera. Al 22%, pagas $62/mes solo en intereses.
        Con tu pago mínimo: 24 meses, $890 en intereses.
        Con $200 extra/mes: 11 meses, $290 en intereses.
        Esto es prioridad #1 antes de cualquier inversión.
```

---

## What Gets Calculated

| Metric | What It Tells You |
|--------|------------------|
| **FI Number** | How much you need to never work again (expenses ÷ 4%) |
| **FI Timeline** | How many years until financial independence |
| **PAW Status** | Are you building wealth faster or slower than expected for your age? |
| **Savings Rate** | The single most important number in personal finance |
| **Debt Payoff Timeline** | Exact months and interest saved with extra payments |
| **Future Value** | What your investments will be worth in 10, 20, 30 years |

---

## Your Data Stays Private

Everything lives on your machine as a plain markdown file at `~/finanzas/<yourname>/perfil.md`. No cloud sync, no database, no third-party service. You own your data completely.

---

## Requirements

- [Claude Code](https://claude.ai/code) (web, desktop, or CLI)
- Python 3.8+ (for calculations)
- `markitdown` — `pip install markitdown` (for file uploads)

---

## Languages

🇺🇸 English · 🇪🇸 Español · 🇫🇷 Français · 🇩🇪 Deutsch · 🇮🇹 Italiano · 🇧🇷 Português · 🇨🇳 中文 · 🇯🇵 日本語

The skill auto-detects your language and responds consistently throughout the session.

---

*Built on the shoulders of Morgan Housel, JL Collins, Thomas Stanley, and James Hughes Jr.*

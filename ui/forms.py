from rich.prompt import Prompt, Confirm, FloatPrompt, IntPrompt
from ui.console import console


def ask(prompt: str, default: str = "") -> str:
    return Prompt.ask(f"[info]{prompt}[/info]", default=default)


def ask_float(prompt: str, default: float = 0.0) -> float:
    raw = Prompt.ask(f"[info]{prompt}[/info]", default=str(default))
    try:
        return float(raw)
    except ValueError:
        console.print("[critical]Valor inválido, usando 0[/critical]")
        return 0.0


def ask_int(prompt: str, default: int = 0) -> int:
    raw = Prompt.ask(f"[info]{prompt}[/info]", default=str(default))
    try:
        return int(raw)
    except ValueError:
        return default


def ask_choice(prompt: str, choices: list, default: str = "") -> str:
    choices_str = " / ".join(choices)
    console.print(f"[muted]Opciones: {choices_str}[/muted]")
    while True:
        val = Prompt.ask(f"[info]{prompt}[/info]", default=default or choices[0])
        if val in choices:
            return val
        console.print(f"[critical]Elige una de: {choices_str}[/critical]")


def ask_bool(prompt: str, default: bool = True) -> bool:
    return Confirm.ask(f"[info]{prompt}[/info]", default=default)


def ask_percent(prompt: str, default: float = 0.0) -> float:
    val = ask_float(f"{prompt} (ej: 18 para 18%)", default * 100)
    return val / 100

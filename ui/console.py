from rich.console import Console
from rich.theme import Theme

_theme = Theme({
    "good": "bold green",
    "warning": "bold yellow",
    "critical": "bold red",
    "info": "bold cyan",
    "muted": "dim white",
    "money": "bold green",
    "debt": "bold red",
    "header": "bold white on blue",
})

console = Console(theme=_theme)

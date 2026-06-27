from rich.console import Console
from rich.live import Live
from rich.panel import Panel

console = Console()

live = Live(refresh_per_second=10)
live.start()

def msg(texto):
    live.update(
        Panel(
            texto,
            title="Sistema de Leilão"
        )
    )

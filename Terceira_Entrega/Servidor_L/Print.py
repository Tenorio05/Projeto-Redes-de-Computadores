from rich.console import Console
from rich.live import Live
from rich.panel import Panel

# Instancia o console da biblioteca "rich" (usada para textos bonitos no terminal)
console = Console()

# Inicia um bloco "Live". Isso permite que o texto na tela do servidor
# seja atualizado dinamicamente na mesma posição, sem "printar" várias linhas para baixo
live = Live(refresh_per_second=10)
live.start()

def msg(texto):
    """
    Função chamada pelo PC_Leilao para atualizar o que está escrito no painel.
    O texto passado será encapsulado dentro de um quadro decorado com o título 'Sistema de Leilão'.
    """
    live.update(
        Panel(
            texto,
            title="Sistema de Leilão"
        )
    )

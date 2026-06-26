

def msg(mensagem):
    # Descobre quantas quebras de linha existem no texto atual
    linhas = mensagem.count('\n')
    
    # Se já tivermos impresso algo antes, esse código faz o cursor 
    # subir de volta o número exato de linhas para reescrever por cima
    if hasattr(msg, "ja_imprimiu") and msg.ja_imprimiu:
        # \033[F sobe uma linha. Multiplicamos pelo número de linhas do texto anterior.
        print(f"\033[{msg.linhas_anteriores}F", end="")
    
    # Imprime o novo texto preenchendo os espaços para não deixar rastro
    # (Dividimos o texto para aplicar o preenchimento de espaços em cada linha dele)
    texto_formatado = "\n".join([f"{linha: <120}" for linha in mensagem.split("\n")])
    print(texto_formatado, end="", flush=True)
    
    # Guarda na memória da função para a próxima vez que ela for chamada
    msg.ja_imprimiu = True
    msg.linhas_anteriores = linhas
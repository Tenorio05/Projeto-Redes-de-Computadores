import os, json, time, base64
import Transmissor as Trsm

# ==========================================
# CONFIGURAÇÕES DE REDE
# ==========================================
HOST = 'localhost'      # IP do Servidor (Para onde os pacotes vão ser enviados/recebidos)
PORT = 8080             # Porta em que o servidor UDP vai escutar
BUFFER_SIZE = 1024      # Tamanho máximo do pacote UDP em bytes
TIMEOUT = 2.0           # Tempo de espera limite para operações de rede (em segundos)

# ==========================================
# DADOS DO LEILÃO
# ==========================================
# Dicionário de arquivos a serem leiloados
# Formato: "id_do_item": ["Nome_do_arquivo", valor_atual, "Nome_do_vencedor_atual"]
arquivos = {
    "1": ["Carro.txt",  1000.0, "ninguem"],
    "2": ["Moto.txt",    500.0, "ninguem"],
    "3": ["Esboco.jpeg", 3000.0, "ninguem"]
}
id_atual = "1" # Define qual item está sendo leiloado no momento

# Dicionário de Compradores conectados
# Formato: endereco_ip_porta: ["Nome_do_usuario", status_de_prontidao_0_ou_1]
Compradores = {}
R_num = 0 # Contador de quantos compradores estão com status "pronto" (ready)

# Variáveis de controle de estado do leilão
Operation = "WAIT" # Pode ser "WAIT" (esperando jogadores) ou "LANCES" (leilão rodando)
num_lances = 0     # Conta quantos lances já foram dados no item atual
tempo_leilao = 0.0 # Guarda a marca de tempo de quando o leilão do item começou


def Lances_init():
    """Inicializa a fase de lances para o próximo item disponível."""
    global Operation, num_lances, tempo_leilao, id_atual
    Operation = "LANCES" # Muda o estado do servidor
    num_lances = 0       # Zera o contador de lances para o novo item
    id_atual = next(iter(arquivos)) # Pega a primeira chave (ID) disponível no dicionário
    tempo_leilao = time.time()      # Registra o momento exato de início (timestamp)
    return


def Funcoes(msg, endereco, udp):
    """Roteador principal: recebe a mensagem do cliente, divide os argumentos e chama a função correta."""
    msg = msg.split("#") # Separa a string pelo caractere '#' (ex: "login#Theo" vira ["login", "Theo"])
    func = msg[0]        # O primeiro elemento é sempre o comando
    F = {"tipo": "text",
         "msg": ""}
    match func:
        case "login":  
            if Operation != "LANCES" : Connect(msg[1], endereco, udp)
            else:
                t = "Não se pode executar essa função durante o Leilao"
                F["msg"] = t
                SendTo(F, endereco, udp)

        case "ready":  
            if Operation != "LANCES" : Ready(endereco, udp)
            else:
                t = "Não se pode executar essa função durante o Leilao"
                F["msg"] = t
                SendTo(F, endereco, udp)
                
        case "bid":    
            if Operation != "WAIT" : Lance(msg[1], msg[2], endereco, udp)
            else:
                t = "Não se pode executar essa função durante o Break"
                F["msg"] = t
                SendTo(F, endereco, udp)

        case "list":   List(endereco, udp)
        case "status": Status(endereco, udp)
        case "logout": 
            if Operation != "LANCES" : Disconnect(endereco, udp)
            else:
                t = "Não se pode executar essa função durante o Leilao"
                F["msg"] = t
                SendTo(F, endereco, udp)
    return


def Connect(nome, endereco, udp):
    """Trata o comando 'login', registrando o usuário."""
    # Verifica se o nome já existe em algum dos valores do dicionário de compradores
    if any(nome == valor[0] for valor in Compradores.values()):
        msg = {"tipo": "text", "msg": "ERRO: este nome ja foi cadastrado"}
    else:
        # Cadastra o novo usuário (0 significa que ele ainda não deu 'ready')
        Compradores[endereco] = [nome, 0]
        msg = {"tipo": "text", "msg": "Voce esta online! Mande o sinal quando estiver pronto para o leilao!"}
    
    SendTo(msg, endereco, udp) # Envia a resposta de volta ao cliente
    return


def Ready(endereco, udp):
    """Trata o comando 'ready', marcando o usuário como pronto para começar."""
    global R_num
    if endereco not in Compradores:
        msg = {"tipo": "text", "msg": "Vc nao esta cadastrado, nao pode executar essa funcao"}
    else:
        Compradores[endereco][1] = 1 # Muda o status do usuário para 1 (Pronto)
        msg = {"tipo": "text", "msg": "Confirmado! Aguarde os outros ficarem prontos"}
        R_num += 1 # Incrementa o número total de pessoas prontas
    
    SendTo(msg, endereco, udp)
    return


def Lance(id, valor, endereco, udp):
    """Trata o comando 'bid', processando e validando uma tentativa de lance."""
    global num_lances
    valor = float(valor) # Converte o valor recebido como string para número decimal

    # Validações antes de aceitar o lance
    if endereco not in Compradores:
        msg = {"tipo": "text", "msg": "Vc nao esta cadastrado, nao pode executar essa funcao"}
        num = 0

    elif id != id_atual:
        msg = {"tipo": "text", "msg": "Lance invalido: este nao e o id do item em leilao no momento"}
        num = 0

    elif arquivos[id][1] >= valor:
        msg = {"tipo": "text", "msg": "Lance invalido: o valor nao superou o valor atual do item"}
        num = 0

    else:
        # Se passou por todas as validações, o lance é aceito
        arquivos[id][1] = valor # Atualiza o valor do item
        arquivos[id][2] = Compradores[endereco][0] # Atualiza o nome do líder atual
        
        # Monta a mensagem que será enviada para TODOS avisando do novo lance
        msg = {"tipo": "text&dado",
               "msg": "Novo lance!",
               "dado": [arquivos[id][1], arquivos[id][2]]
               }
        num_lances += 1 # Incrementa o contador de lances deste item
        num = 1

    # Se o lance for inválido, envia o erro apenas para quem tentou dar o lance
    if not num:
        SendTo(msg, endereco, udp)
        return

    # Se o lance for válido, faz um broadcast (envia a novidade para todos os clientes conectados)
    for i in Compradores:
        SendTo(msg, i, udp)
    return


def List(endereco, udp):
    """Trata o comando 'list', enviando os itens disponíveis."""
    if endereco not in Compradores:
        msg = {"tipo": "text", "msg": "Vc nao esta cadastrado, nao pode executar essa funcao"}
    else:
        # Cria um novo dicionário contendo apenas o Nome e Valor (ignora quem está vencendo)
        arquivos_f = {key: valor[:2] for key, valor in arquivos.items()}
        msg = {"tipo": "text&dado",
               "msg": "Aqui estao os itens ainda em estoque para leilao",
               "dado": arquivos_f
               }
    SendTo(msg, endereco, udp)
    return


def Status(endereco, udp):
    """Trata o comando 'status', informando quem está ganhando o item atual."""
    if endereco not in Compradores:
        msg = {"tipo": "text", "msg": "Vc nao esta cadastrado, nao pode executar essa funcao"}
    elif Operation != "LANCES":
        msg = {"tipo": "text", "msg": "O leilao ainda nao iniciou"}
    else:
        msg = {"tipo": "text&dado",
               "msg": "Quem esta vencendo no leilao atual",
               "dado": arquivos[id_atual][2] # Pega o nome do vencedor do item atual
               }
    SendTo(msg, endereco, udp)
    return


def Disconnect(endereco, udp):
    """Trata o comando 'logout', removendo o usuário do servidor."""
    if endereco in Compradores:
        del Compradores[endereco] # Remove do dicionário
        msg = {"tipo": "text", "msg": "Desconectado com sucesso! Obrigado por participar!"}
        SendTo(msg, endereco, udp)
    return


def SendTo(dado, endereco, udp):
    """Função auxiliar para converter dicionários em JSON e enviar usando protocolo RDT."""
    data = json.dumps(dado).encode('utf-8') # Converte para JSON e codifica em bytes
    Trsm.SendArquive(data, endereco, BUFFER_SIZE, udp) # Envia usando a sua classe Transmissor
    return


def FimDeLeilao(udp):
    """Lógica acionada quando o tempo acaba ou o limite de lances é atingido."""
    global Operation, R_num
   
    for i in Compradores:
        # Verifica se o cliente atual no loop é o ganhador
        if Compradores[i][0] == arquivos[id_atual][2]:
            
            # Abre o arquivo ganho em modo de leitura binária
            with open(arquivos[id_atual][0], 'rb') as f:
                while True:
                    bloco = f.read(400) # Lê de 400 em 400 bytes para não estourar o limite UDP
                    if not bloco:
                        break # Se não houver mais dados, sai do loop
                    
                    # Constrói o pacote com o pedaço do arquivo
                    msg = {
                        "tipo": "text&arquivo",
                        "msg": f"Parabens! Voce conseguiu o {arquivos[id_atual][0]}!",
                        "nome": arquivos[id_atual][0],
                        "dados": base64.b64encode(bloco).decode() # Converte os bytes puros para string Base64
                    }
                    SendTo(msg, i, udp) # Envia o bloco ao ganhador
                    
            # Avisa o cliente que o envio do arquivo acabou
            SendTo({"tipo": "fim_arquivo"}, i, udp)
            
        else:
            # Avisa aos perdedores que não ganharam este item
            msg = {"tipo": "text",
                   "msg": "Mais sorte na proxima! Enviando o arquivo para o ganhador, aguarde..."}
            SendTo(msg, i, udp)

    # Reinicia as variáveis para preparar para o próximo item
    Operation = "WAIT"
    R_num = 0
    del arquivos[id_atual] # Remove o item que acabou de ser vendido da lista
    
    # Reseta o status de prontidão de todos para 0
    for i in Compradores:
        Compradores[i][1] = 0
    return

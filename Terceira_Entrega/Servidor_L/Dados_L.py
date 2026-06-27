import os, json, time, base64
import Transmissor as Trsm

HOST = 'localhost'      # IP do Servidor (Para onde os ficheiros vão ser enviados)
PORT = 8080             # A mesma porta que foi configurada no servidor
BUFFER_SIZE = 1024      # Tamanho do pacote
TIMEOUT = 2.0           # Tempo de espera limite


# Lista de arquivos a serem leiloados
# modelo: id:[nome do arquivo, valor, nome do ultimo a dar lance valido]
arquivos = {
    "1": ["Carro.txt",  1000.0, "ninguem"],
    "2": ["Moto.txt",    500.0, "ninguem"],
    "3": ["Esboco.jpeg", 3000.0, "ninguem"]
}
id_atual = "1"

# Lista de Compradores participando do leilão
# modelo: endereco:[nome, estado de prontidão]
Compradores = {}
R_num = 0

# Status de operação do leilão
Operation = "WAIT"
num_lances = 0
tempo_leilao = 0.0


def Lances_init():
    global Operation, num_lances, tempo_leilao, id_atual
    Operation = "LANCES"
    num_lances = 0
    id_atual = next(iter(arquivos))
    tempo_leilao = time.time()
    return


def Funcoes(msg, endereco, udp):
    msg = msg.split("#")
    func = msg[0]
    match func:
        case "login":  Connect(msg[1], endereco, udp)
        case "ready":  Ready(endereco, udp)
        case "bid":    Lance(msg[1], msg[2], endereco, udp)
        case "list":   List(endereco, udp)
        case "status": Status(endereco, udp)
        case "logout": Disconnect(endereco, udp)
    return


def Connect(nome, endereco, udp):
    if any(nome == valor[0] for valor in Compradores.values()):
        msg = {"tipo": "text",
               "msg": "ERRO: este nome ja foi cadastrado"}
    else:
        Compradores[endereco] = [nome, 0]
        msg = {"tipo": "text",
               "msg": "Voce esta online! Mande o sinal quando estiver pronto para o leilao!"}
    SendTo(msg, endereco, udp)
    return


def Ready(endereco, udp):
    global R_num
    if endereco not in Compradores:
        msg = {"tipo": "text",
               "msg": "Vc nao esta cadastrado, nao pode executar essa funcao"}
    else:
        Compradores[endereco][1] = 1
        msg = {"tipo": "text",
               "msg": "Confirmado! Aguarde os outros ficarem prontos"}
        R_num += 1
    SendTo(msg, endereco, udp)
    return


def Lance(id, valor, endereco, udp):
    global num_lances
    valor = float(valor)

    if endereco not in Compradores:
        msg = {"tipo": "text",
               "msg": "Vc nao esta cadastrado, nao pode executar essa funcao"}
        num = 0

    elif id != id_atual:
        msg = {"tipo": "text",
               "msg": "Lance invalido: este nao e o id do item em leilao no momento"}
        num = 0

    elif arquivos[id][1] >= valor:
        msg = {"tipo": "text",
               "msg": "Lance invalido: o valor nao superou o valor atual do item"}
        num = 0

    else:
        arquivos[id][1] = valor
        arquivos[id][2] = Compradores[endereco][0]
        msg = {"tipo": "text&dado",
               "msg": "Novo lance!",
               "dado": [arquivos[id][1], arquivos[id][2]]
               }
        num_lances += 1
        num = 1

    if not num:
        SendTo(msg, endereco, udp)
        return

    for i in Compradores:
        SendTo(msg, i, udp)
    return


def List(endereco, udp):
    if endereco not in Compradores:
        msg = {"tipo": "text",
               "msg": "Vc nao esta cadastrado, nao pode executar essa funcao"}
    else:
        arquivos_f = {key: valor[:2] for key, valor in arquivos.items()}
        msg = {"tipo": "text&dado",
               "msg": "Aqui estao os itens ainda em estoque para leilao",
               "dado": arquivos_f
               }
    SendTo(msg, endereco, udp)
    return


def Status(endereco, udp):
    if endereco not in Compradores:
        msg = {"tipo": "text",
               "msg": "Vc nao esta cadastrado, nao pode executar essa funcao"}
    elif Operation != "LANCES":
        msg = {"tipo": "text",
               "msg": "O leilao ainda nao iniciou"}
    else:
        msg = {"tipo": "text&dado",
               "msg": "Quem esta vencendo no leilao atual",
               "dado": arquivos[id_atual][2]
               }
    SendTo(msg, endereco, udp)
    return


def Disconnect(endereco, udp):
    if endereco in Compradores:
        del Compradores[endereco]
        msg = {"tipo": "text",
               "msg": "Desconectado com sucesso! Obrigado por participar!"}
        SendTo(msg, endereco, udp)
    return


def SendTo(dado, endereco, udp):
    data = json.dumps(dado).encode('utf-8')
    Trsm.SendArquive(data, endereco, BUFFER_SIZE, udp)
    return


def FimDeLeilao(udp):
    global Operation, R_num
   
    for i in Compradores:
        print(i)
        if Compradores[i][0] == arquivos[id_atual][2]:
            
            with open(arquivos[id_atual][0], 'rb') as f:
                while True:
                    bloco = f.read(400)
                    if not bloco:
                        break
                    msg = {
                        "tipo": "text&arquivo",
                        "msg": f"Parabens! Voce conseguiu o {arquivos[id_atual][0]}!",
                        "nome": arquivos[id_atual][0],
                        "dados": base64.b64encode(bloco).decode()
                    }
                    SendTo(msg, i, udp)
            SendTo({"tipo": "fim_arquivo"}, i, udp)
        else:
            msg = {"tipo": "text",
                   "msg": "Mais sorte na proxima! Enviando o arquivo para o ganhador, aguarde..."}
            SendTo(msg, i, udp)

    Operation = "WAIT"
    R_num = 0
    del arquivos[id_atual]
    for i in Compradores:
        Compradores[i][1] = 0
    return

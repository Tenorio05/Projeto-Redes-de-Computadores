import socket
import json
import base64
import threading
import time
import Transmissor as Trsm
import Receptor as Rcpt

HOST = 'localhost'
PORT = 8080
BUFFER_SIZE = 1024
TIMEOUT = 2.0

SERVIDOR = (HOST, PORT)

# Lock que serializa o acesso ao socket entre o thread principal e o thread receptor
socket_lock = threading.Lock()

# Sinaliza ao thread receptor que deve encerrar
running = True

# Arquivo sendo recebido no momento (None quando não há transferência ativa)
arquivo_em_recebimento = None


def handle_message(dados):
    """Interpreta e exibe qualquer mensagem JSON recebida do servidor."""
    global arquivo_em_recebimento

    tipo = dados.get("tipo", "")

    if tipo == "text":
        print(f"\n[Servidor] {dados['msg']}")

    elif tipo == "text&dado":
        print(f"\n[Servidor] {dados['msg']}")
        dado = dados["dado"]

        if isinstance(dado, list):
            # Novo lance: dado = [valor, comprador]
            print(f"  Valor atual : R$ {dado[0]:.2f}")
            print(f"  Comprador   : {dado[1]}")

        elif isinstance(dado, dict):
            # Listagem de itens: dado = {"id": [nome, valor], ...}
            print("  +---------+----------------------+-------------+")
            print("  |   ID    | Item                 | Valor atual |")
            print("  +---------+----------------------+-------------+")
            for id_item, info in dado.items():
                print(f"  | {id_item:<7} | {info[0]:<20} | R$ {info[1]:<8.2f}|")
            print("  +---------+----------------------+-------------+")

        else:
            # Status: dado = nome do vencedor
            print(f"  Liderando: {dado}")

    elif tipo == "text&arquivo":
        print(f"\n[Servidor] {dados['msg']}")
        nome = dados["nome"]
        bloco = base64.b64decode(dados["dados"])
        with open(nome, "ab") as f:
            f.write(bloco)
        arquivo_em_recebimento = nome

    elif tipo == "fim_arquivo":
        if arquivo_em_recebimento:
            print(f"\n[Cliente] Arquivo '{arquivo_em_recebimento}' recebido com sucesso!")
            arquivo_em_recebimento = None

    else:
        # Tipo desconhecido: exibe o conteúdo bruto
        print(f"\n[Servidor] {dados}")


def receive_one(udp):
    """
    Tenta receber e processar uma mensagem do servidor.
    Usa timeout curto para não segurar o lock por muito tempo.
    Retorna True se recebeu algo, False em timeout.
    """
    udp.settimeout(0.15)
    try:
        raw, addr = udp.recvfrom(BUFFER_SIZE)
        num, msg = Rcpt.GetMsg(udp, raw, addr)
        if num:
            dados = json.loads(msg)
            handle_message(dados)
        return True
    except (socket.timeout, OSError):
        return False
    finally:
        udp.settimeout(TIMEOUT)


def receptor_thread(udp):
    """
    Thread que fica escutando mensagens espontâneas do servidor
    (ex: lances de outros compradores) enquanto o usuário está digitando.
    """
    global running
    while running:
        # Tenta adquirir o lock sem bloquear por muito tempo
        acquired = socket_lock.acquire(timeout=0.05)
        if acquired:
            try:
                receive_one(udp)
            finally:
                socket_lock.release()
        # Pausa mínima para ceder CPU ao thread principal quando necessário
        time.sleep(0.01)


def send_and_receive(udp, comando):
    """
    Envia um comando ao servidor e aguarda a resposta imediata,
    mantendo o lock durante todo o ciclo send→receive.
    """
    with socket_lock:
        data = comando.encode('utf-8')
        Trsm.SendArquive(data, SERVIDOR, BUFFER_SIZE, udp)

        # Recebe a resposta direta do servidor (pode ser 1 ou mais pacotes)
        udp.settimeout(TIMEOUT)
        while True:
            try:
                raw, addr = udp.recvfrom(BUFFER_SIZE)
                num, msg = Rcpt.GetMsg(udp, raw, addr)
                if not num:
                    continue
                dados = json.loads(msg)
                handle_message(dados)

                # Se estava recebendo arquivo, continua até "fim_arquivo"
                if dados.get("tipo") == "text&arquivo":
                    while True:
                        raw, addr = udp.recvfrom(BUFFER_SIZE)
                        num, msg = Rcpt.GetMsg(udp, raw, addr)
                        if not num:
                            continue
                        dados = json.loads(msg)
                        handle_message(dados)
                        if dados.get("tipo") == "fim_arquivo":
                            break
                break
            except socket.timeout:
                break


def iniciar_cliente():
    global running

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Deixa o SO escolher uma porta livre, garantindo portas únicas por instância
    udp.bind(('', 0))
    udp.settimeout(TIMEOUT)

    porta_local = udp.getsockname()[1]
    print("=" * 45)
    print("       AuctionCIn - Cliente de Leilao")
    print("=" * 45)
    print(f"Conectado na porta local: {porta_local}")
    print("\nComandos disponíveis:")
    print("  login <nome>      — entrar no leilao")
    print("  ready             — sinalizar prontidao")
    print("  bid <id> <valor>  — dar um lance")
    print("  list              — ver itens disponiveis")
    print("  status            — ver quem esta ganhando")
    print("  logout            — sair do sistema")
    print("-" * 45)

    # Inicia o thread que escuta mensagens espontâneas
    t = threading.Thread(target=receptor_thread, args=(udp,), daemon=True)
    t.start()

    try:
        while True:
            try:
                entrada = input("\n> ").strip()
            except EOFError:
                break

            if not entrada:
                continue

            partes = entrada.split()
            cmd = partes[0].lower()

            if cmd == "login" and len(partes) == 2:
                send_and_receive(udp, f"login#{partes[1]}")

            elif cmd == "ready":
                send_and_receive(udp, "ready")

            elif cmd == "bid" and len(partes) == 3:
                send_and_receive(udp, f"bid#{partes[1]}#{partes[2]}")

            elif cmd == "list":
                send_and_receive(udp, "list")

            elif cmd == "status":
                send_and_receive(udp, "status")

            elif cmd == "logout":
                send_and_receive(udp, "logout")
                print("[Cliente] Desconectado. Encerrando.")
                break

            else:
                print("[Cliente] Comando invalido. Use: login, ready, bid, list, status, logout")

    except KeyboardInterrupt:
        print("\n[Cliente] Encerrado pelo usuario.")

    finally:
        running = False
        udp.close()


if __name__ == "__main__":
    iniciar_cliente()

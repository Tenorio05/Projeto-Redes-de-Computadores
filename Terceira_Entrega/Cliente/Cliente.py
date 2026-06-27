import socket
import json
import base64
import threading
import time
import Transmissor as Trsm
import Receptor as Rcpt

# ==========================================
# CONFIGURAÇÕES DO CLIENTE
# ==========================================
HOST = 'localhost'
PORT = 8080
BUFFER_SIZE = 1024
TIMEOUT = 2.0

SERVIDOR = (HOST, PORT)

# Lock que serializa o acesso ao socket entre o thread principal (que envia dados) 
# e o thread receptor (que fica escutando a rede). Impede "batidas de cabeça".
socket_lock = threading.Lock()

# Flag que sinaliza à thread receptora que o programa está rodando. Se for False, a thread morre.
running = True

# Variável de controle para guardar o nome do arquivo que está sendo baixado (None se não estiver baixando nada)
arquivo_em_recebimento = None


def handle_message(dados):
    """Interpreta e exibe qualquer mensagem JSON recebida do servidor de forma amigável no console."""
    global arquivo_em_recebimento

    tipo = dados.get("tipo", "") # Verifica qual o 'tipo' da mensagem vinda no JSON

    if tipo == "text":
        # Mensagens de texto comuns (Avisos, erros, confirmações)
        print(f"\n[Servidor] {dados['msg']}")

    elif tipo == "text&dado":
        # Mensagens que trazem texto e uma carga de dados (listas, objetos)
        print(f"\n[Servidor] {dados['msg']}")
        dado = dados["dado"]

        if isinstance(dado, list):
            # Formata a exibição de um "Novo lance": dado = [valor, comprador]
            print(f"  Valor atual : R$ {dado[0]:.2f}")
            print(f"  Comprador   : {dado[1]}")

        elif isinstance(dado, dict):
            # Formata a exibição da listagem de itens do comando "list"
            print("  +---------+----------------------+-------------+")
            print("  |   ID    | Item                 | Valor atual |")
            print("  +---------+----------------------+-------------+")
            for id_item, info in dado.items():
                print(f"  | {id_item:<7} | {info[0]:<20} | R$ {info[1]:<8.2f}|")
            print("  +---------+----------------------+-------------+")

        else:
            # Formata a exibição de Status (dado traz apenas uma string com o nome do líder)
            print(f"  Liderando: {dado}")

    elif tipo == "text&arquivo":
        # Recebendo os pedaços (blocos) do prêmio
        if not arquivo_em_recebimento:
            print(f"\n[Servidor] {dados['msg']}") # Imprime a msg só no primeiro bloco
            
        nome = dados["nome"]
        # Decodifica a string Base64 enviada pelo servidor, transformando-a novamente em bytes puros
        bloco = base64.b64decode(dados["dados"])
        
        # Abre o arquivo em modo "append binary" (ab), adicionando os novos bytes ao final do arquivo
        with open(nome, "ab") as f:
            f.write(bloco)
            
        arquivo_em_recebimento = nome # Sinaliza que o download está em andamento

    elif tipo == "fim_arquivo":
        # Aviso de que a transferência do item inteiro foi concluída
        if arquivo_em_recebimento:
            print(f"\n[Cliente] Arquivo '{arquivo_em_recebimento}' recebido com sucesso!")
            arquivo_em_recebimento = None # Zera o controle de download

    else:
        # Se vier um tipo desconhecido, imprime o JSON puro (fallback de segurança)
        print(f"\n[Servidor] {dados}")


def receive_one(udp):
    """
    Tenta receber e processar apenas UMA mensagem do servidor.
    Retorna True se receber algo, False se der timeout.
    """
    udp.settimeout(0.15) # Timeout super curto para não travar o terminal se não houver mensagens
    try:
        raw, addr = udp.recvfrom(BUFFER_SIZE)
        num, msg = Rcpt.GetMsg(udp, raw, addr) # Passa pela validação do RDT
        if num:
            dados = json.loads(msg) # Transforma a string recebida de volta em um dicionário Python
            handle_message(dados)   # Joga para a função tratadora
        return True
    except (socket.timeout, OSError):
        return False
    finally:
        udp.settimeout(TIMEOUT) # Retorna o timeout ao normal


def receptor_thread(udp):
    """
    Essa thread roda em paralelo 100% do tempo. Ela fica escutando a rede
    para receber notificações espontâneas (ex: alguém deu um lance, ou o leilão acabou)
    mesmo enquanto você está digitando outro comando.
    """
    global running
    while running:
        # Tenta pegar a "chave" (lock) do socket. Se a thread principal estiver
        # enviando/recebendo comando agora, essa thread aguarda.
        acquired = socket_lock.acquire(timeout=0.05)
        if acquired:
            try:
                receive_one(udp) # Se pegou o lock, escuta a rede
            finally:
                socket_lock.release() # Devolve a chave
        
        # Pausa mínima para não consumir 100% de CPU à toa
        time.sleep(0.01)


def send_and_receive(udp, comando):
    """
    Envia o comando formatado para o servidor e retém a prioridade da rede
    até receber as respostas imediatas.
    """
    with socket_lock: # Pega o lock. Enquanto estiver aqui dentro, a receptor_thread não escuta nada
        data = comando.encode('utf-8')
        Trsm.SendArquive(data, SERVIDOR, BUFFER_SIZE, udp) # Envia usando RDT 3.0

        udp.settimeout(TIMEOUT)
        while True:
            try:
                # Aguarda a resposta do servidor
                raw, addr = udp.recvfrom(BUFFER_SIZE)
                num, msg = Rcpt.GetMsg(udp, raw, addr)
                if not num:
                    continue
                
                dados = json.loads(msg)
                handle_message(dados)

                # Tratamento especial: Se o servidor começou a mandar um arquivo,
                # o cliente prende a conexão aqui no loop até o servidor mandar o "fim_arquivo"
                if dados.get("tipo") == "text&arquivo":
                    while True:
                        raw, addr = udp.recvfrom(BUFFER_SIZE)
                        num, msg = Rcpt.GetMsg(udp, raw, addr)
                        if not num: continue
                        
                        dados = json.loads(msg)
                        handle_message(dados)
                        if dados.get("tipo") == "fim_arquivo":
                            break # Sai do loop de arquivo
                
                break # Sai do loop de recebimento principal, comando finalizado
            
            except socket.timeout:
                break # Se não recebeu resposta, apenas segue a vida


def iniciar_cliente():
    global running

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Porta 0 indica ao sistema operacional para fornecer a primeira porta disponível, 
    # permitindo abrir múltiplos clientes na mesma máquina sem dar conflito
    udp.bind(('', 0))
    udp.settimeout(TIMEOUT)

    porta_local = udp.getsockname()[1]
    
    # Exibe menu inicial
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

    # Inicia a thread receptora que vigiará eventos assíncronos
    t = threading.Thread(target=receptor_thread, args=(udp,), daemon=True)
    t.start()

    try:
        while True:
            try:
                # Fica travado esperando o usuário digitar no terminal
                entrada = input("\n> ").strip()
            except EOFError:
                break

            if not entrada:
                continue

            # Quebra a entrada e verifica qual comando o usuário digitou
            partes = entrada.split()
            cmd = partes[0].lower()

            if cmd == "login" and len(partes) == 2:
                send_and_receive(udp, f"login#{partes[1]}") # Junta com '#' seguindo o protocolo

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
                break # Sai do while True e o programa termina

            else:
                print("[Cliente] Comando invalido. Use: login, ready, bid, list, status, logout")

    except KeyboardInterrupt:
        # Se o usuário der Ctrl+C, o programa desliga de forma segura
        print("\n[Cliente] Encerrado pelo usuario.")

    finally:
        running = False # Manda a thread receptora morrer
        udp.close()     # Libera a porta de rede


if __name__ == "__main__":
    iniciar_cliente()

# ==================================================
# IMPLEMENTAÇÃO DO SERVIDOR (RDT 3.0)
# ==================================================

import socket
import os
import Receptor_S as Receptor, Transmissor_S as Transmissor

HOST = '192.168.1.110'  # IP do Servidor (Onde este código está a correr)
PORT = 1044             # Porta aberta para escutar as ligações (Port Forwarding necessário para internet externa)
BUFFER_SIZE = 1024      # Tamanho máximo de cada pacote UDP (Em bytes)
TIMEOUT = 2.0           # Tempo limite em segundos para considerar que um pacote se perdeu

def iniciar_servidor():
    # Cria o socket do tipo UDP (SOCK_DGRAM) usando endereçamento IPv4 (AF_INET)
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Define o temporizador do socket. Se passar este tempo sem receber nada, dá TimeoutError
    udp.settimeout(TIMEOUT)
    
    # Liga o socket ao IP e à porta escolhida para começar a escutar
    udp.bind((HOST, PORT))
    print(f"[SERVIDOR] Servidor UDP a rodar em {HOST}:{PORT}...\n")

    while True:
        try:
            print("[SERVIDOR] Aguardando recebimento de ficheiros...")
            
            # 1. FICA À ESCUTA: Recebe o primeiro pacote (que contém o nome do ficheiro)
            B_msg, endereco_cliente = udp.recvfrom(BUFFER_SIZE)

            # Extrai o nome do ficheiro usando a função do Receptor.
            # Retorna 0 se for um pacote repetido/inválido.
            num, nome_arquivo_servidor, nome_arquivo = Receptor.GetArquiveName(udp, B_msg, endereco_cliente, "SERVER", "servidor")
            if num == 0: continue # Se for duplicado, ignora e volta ao topo do loop
            
            # 2. RECEBE OS DADOS: Entra no loop para receber o conteúdo do ficheiro
            Receptor.GetArquiveData(udp, nome_arquivo_servidor, BUFFER_SIZE, endereco_cliente)
                    
            print(f"[SERVIDOR] Ficheiro '{nome_arquivo_servidor}' guardado no servidor com sucesso!")

            # 3. DEVOLUÇÃO: Agora o servidor troca de papel e vira remetente
            print("[SERVIDOR] A iniciar a devolução do ficheiro para o cliente...")
            
            # Primeiro envia o nome original do ficheiro para o cliente saber o que está a receber
            data = nome_arquivo.encode('utf-8')
            Transmissor.SendArquive(data, endereco_cliente, BUFFER_SIZE, udp)

            # Abre o arquivo que acabou de gravar em modo de leitura binária ('rb')
            with open(nome_arquivo_servidor, 'rb') as f:
                while True:
                    # Lê pedaços do ficheiro (deixando 10 bytes de espaço para o cabeçalho do RDT)
                    data = f.read(BUFFER_SIZE-10)
                    
                    # Se não houver mais nada para ler, quebra o loop
                    if not data: break

                    # Envia o pedaço de dados
                    Transmissor.SendArquive(data, endereco_cliente, BUFFER_SIZE, udp)
            
            # Envia a flag 'FIM' para avisar o cliente que o ficheiro acabou
            Transmissor.SendArquive(b'FIM', endereco_cliente, BUFFER_SIZE, udp)
            print("[SERVIDOR] Ficheiro devolvido com sucesso!\n")

        # Exceção tratada para que o servidor não feche se ninguém enviar ficheiros em 2 segundos
        except (socket.timeout, TimeoutError):
            continue 

        # Encerra graciosamente se o utilizador pressionar Ctrl+C no terminal
        except KeyboardInterrupt:
            print("\n[SERVIDOR] Servidor encerrado pelo utilizador.")
            break

    # Fecha a ligação ao socket ao sair do programa
    udp.close()

if __name__ == "__main__":
    iniciar_servidor()
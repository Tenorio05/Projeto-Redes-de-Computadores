# ==================================================
# IMPLEMENTAÇÃO DO SERVIDOR
# ==================================================

import socket
import os
import Receptor, Transmissor

HOST = '192.168.1.110'      # IP do Servidor
PORT = 1044             # Porta onde o servidor vai "escutar" 
BUFFER_SIZE = 1024
TIMEOUT = 2.0

def iniciar_servidor():
    # Cria o socket do servidor
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.settimeout(TIMEOUT)
    udp.bind((HOST, PORT))
    print(f"[SERVIDOR] Servidor UDP rodando em {HOST}:{PORT}...\n")

    while True:
        try:
            print("[SERVIDOR] Aguardando recebimento de arquivos...")
            
            # Recebe o nome/extensão do arquivo
            B_msg, endereco_cliente = udp.recvfrom(BUFFER_SIZE)

            num, nome_arquivo_servidor, nome_arquivo = Receptor.GetArquiveName(udp, B_msg, endereco_cliente, "SERVER", "servidor")
            if num == 0: continue
            
            # Recebe e salva o conteúdo do arquivo
            Receptor.GetArquiveData(udp, nome_arquivo_servidor, BUFFER_SIZE, endereco_cliente)
                    
            print(f"[SERVIDOR] Arquivo '{nome_arquivo_servidor}' salvo no servidor!")

            # Devolve o arquivo p/ o cliente
            print("[SERVIDOR] Iniciando a devolução do arquivo para o cliente...")
            
            # Diz ao cliente o nome do arquivo que está voltando
            data = nome_arquivo.encode('utf-8')
            Transmissor.SendArquive(data, endereco_cliente, BUFFER_SIZE, udp)

            # Abre o arquivo recém-salvo
            with open(nome_arquivo_servidor, 'rb') as f:
                while True:
                    data = f.read(BUFFER_SIZE-10)
                    if not data: break

                    Transmissor.SendArquive(data, endereco_cliente, BUFFER_SIZE, udp)
            
            Transmissor.SendArquive(b'FIM', endereco_cliente, BUFFER_SIZE, udp)
            print("[SERVIDOR] Arquivo devolvido com sucesso!\n")

        except (socket.timeout, TimeoutError):
            continue # O tempo acabou, mas apenas volte a escutar!

        except KeyboardInterrupt:
            print("\n[SERVIDOR] Servidor encerrado pelo usuário.")
            break

    # Fecha a conexão ao sair do loop
    udp.close()

if __name__ == "__main__":
    iniciar_servidor()
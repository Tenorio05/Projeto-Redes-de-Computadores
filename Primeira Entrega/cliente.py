# ==================================================
# IMPLEMENTAÇÃO DO CLIENTE
# ==================================================

import socket
import os

HOST = '172.20.18.24'      # IP do servidor
PORT = 1044                # A mesma porta configurada no servidor
BUFFER_SIZE = 1024

TXT = 'teste.txt'
PNG = 'kurose.png'
PDF = 'AuctionCIn.pdf'
MP3_1 = 'nggyu.mp3'
MP3_2 = 'shaaaw.mp3'

I = 4

def iniciar_cliente():
    # Cria lista para simplificar
    ARQ = [TXT, PNG, PDF, MP3_1, MP3_2]

    # Verifica se o arquivo realmente existe no PC
    if not os.path.exists(ARQ[I]):
        print(f"[ERRO] O arquivo '{ARQ[I]}' não foi encontrado na pasta atual.")
        return

    destino = (HOST, PORT)

    # Cria o socket do cliente
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"[CLIENTE] Iniciando transferência do arquivo: {ARQ[I]}")

    # Envia o nome do arquivo
    udp.sendto(ARQ[I].encode('utf-8'), destino)

    # Lê e envia o arquivo em partes (como faria o Edward)
    with open(ARQ[I], 'rb') as f:
        pedaco = f.read(BUFFER_SIZE)
        while pedaco:
            udp.sendto(pedaco, destino)
            pedaco = f.read(BUFFER_SIZE)
        
        udp.sendto(b'', destino)  # sinaliza o fim do envio (EOF)
    
    print("[CLIENTE] Arquivo enviado. Aguardando a devolução pelo servidor...")

    # Recebe o arquivo de resposta do servidor
    msg_nome, _ = udp.recvfrom(BUFFER_SIZE)  # nome do arquivo que está voltando
    nome_recebido = msg_nome.decode('utf-8')
    
    # Abre um novo arquivo em 'wb' (escrita binária) para salvar o que chegar
    with open(nome_recebido, 'wb') as f:
        while True:
            dados, _ = udp.recvfrom(BUFFER_SIZE)
            
            # Se receber pacote vazio, o servidor terminou de devolver
            if not dados:
                break
            
            f.write(dados)
    
    print(f"[CLIENTE] Sucesso! O arquivo voltou e foi salvo como: '{nome_recebido}'")

    # Encerra o socket
    udp.close()

if __name__ == "__main__":
    iniciar_cliente()
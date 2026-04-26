# ==================================================
# IMPLEMENTAÇÃO DO CLIENTE
# ==================================================

import socket
import os

HOST = '127.0.0.1'   # IP do servidor
PORT = 1044          # A mesma porta configurada no servidor
BUFFER_SIZE = 1024

TXT = 'teste.txt'
PNG = 'kurose.png'
PDF = 'AuctionCIn.pdf'

def iniciar_cliente():
    # Cria lista para simplificar
    # ARQUIVOS = [TXT, PNG, PDF]

    # Verifica se o arquivo realmente existe no PC
    if not os.path.exists(TXT):
        print(f"[ERRO] O arquivo '{TXT}' não foi encontrado na pasta atual.")
        return

    destino = (HOST, PORT)

    # Cria o socket do cliente
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"[CLIENTE] Iniciando transferência do arquivo: {TXT}")

    # Envia o nome do arquivo
    udp.sendto(TXT.encode('utf-8'), destino)

    # Lê e envia o arquivo em partes (como faria o Edward)
    with open(TXT, 'rb') as f:
        pedaco = f.read(BUFFER_SIZE)
        while pedaco:
            udp.sendto(pedaco, destino)
            pedaco = f.read(BUFFER_SIZE)
        
        udp.sendto(b'', destino)  # sinaliza o fim do envio (EOF)
    
    print("[CLIENTE] Arquivo enviado. Aguardando a devolução pelo servidor...")

    # Recebe o arquivo de resposta do servidor
    msg_nome, _ = udp.recvfrom(BUFFER_SIZE)  # nome do arquivo que está voltando
    nome_recebido = msg_nome.decode('utf-8')
    
    # Adiciona um prefixo para não sobrescrever o seu arquivo original!
    nome_arquivo_final = f"leilao_{nome_recebido}"

    # Abre um novo arquivo em 'wb' (escrita binária) para salvar o que chegar
    with open(nome_arquivo_final, 'wb') as f:
        while True:
            dados, _ = udp.recvfrom(BUFFER_SIZE)
            
            # Se receber pacote vazio, o servidor terminou de devolver
            if not dados:
                break
            
            f.write(dados)
    
    print(f"[CLIENTE] Sucesso! O arquivo voltou e foi salvo como: '{nome_arquivo_final}'")

    # Encerra o socket
    udp.close()

if __name__ == "__main__":
    iniciar_cliente()
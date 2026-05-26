# ==================================================
# IMPLEMENTAÇÃO DO CLIENTE (RDT 3.0)
# ==================================================

import socket
import os
import Receptor_C as Receptor, Transmissor_C as Transmissor

HOST = '10.39.44.149'    # IP do Servidor (Para onde os ficheiros vão ser enviados)
PORT = 1044             # A mesma porta que foi configurada no servidor
BUFFER_SIZE = 1024      # Tamanho do pacote
TIMEOUT = 2.0           # Tempo de espera limite

# Lista de ficheiros que o cliente vai tentar enviar
arquivos = [
    'teste.txt',
    'bianca-cel.jpg',
    'AuctionCIn.pdf',
    'nggyu.mp3',
    'shaaaw.mp3',
    'auramaisego.mp3'
]

def iniciar_cliente():
    # Define o tuplo de destino (IP, Porta)
    destino = (HOST, PORT)

    # Cria o socket UDP e aplica o tempo limite
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.settimeout(TIMEOUT)

    # Loop principal que percorre cada ficheiro da lista
    for i in range(len(arquivos)):

        # Segurança: Verifica se o ficheiro realmente existe no PC antes de tentar enviar
        if not os.path.exists(arquivos[i]):
            print(f"[ERRO] O ficheiro '{arquivos[i]}' não foi encontrado na pasta atual.")
            continue

        print(f"[CLIENTE] Iniciando transferência do ficheiro: {arquivos[i]}")

        # 1. ENVIO DO NOME: Converte o nome para bytes e envia
        data = arquivos[i].encode('utf-8')
        Transmissor.SendArquive(data, destino, BUFFER_SIZE, udp)

        # 2. ENVIO DOS DADOS: Abre o ficheiro e lê em binário
        with open(arquivos[i], 'rb') as f:
                while True:
                    # Lê até 1014 bytes de cada vez
                    data = f.read(BUFFER_SIZE-10)
                    if not data: break
                    
                    # Usa o transmissor para enviar o pedaço e aguardar o ACK
                    Transmissor.SendArquive(data, destino, BUFFER_SIZE, udp)
        
        # 3. FIM DO ENVIO: Avisa o servidor que já não há mais pacotes para este ficheiro
        Transmissor.SendArquive(b'FIM', destino, BUFFER_SIZE, udp)
        print("[CLIENTE] Ficheiro enviado. Aguardando o retorno do servidor...")

        # 4. RECEÇÃO DO RETORNO: Loop de espera segura para receber o ficheiro de volta
        while True:
            try:
                print("[CLIENTE] Aguardando a devolução do ficheiro...")
                    
                # Recebe o pacote com o nome do ficheiro (ou a flag de que vai iniciar)
                B_msg, endereco_cliente = udp.recvfrom(BUFFER_SIZE)

                # Processa o pacote recebido
                num, nome_guardado, nome_arquivo = Receptor.GetArquiveName(udp, B_msg, endereco_cliente, "CLIENTE", "leilao")
                if num == 0: continue # Se for lixo/duplicado, ignora
                
                # Fica preso nesta função a receber pedaço a pedaço até o servidor mandar o 'FIM'
                Receptor.GetArquiveData(udp, nome_guardado, BUFFER_SIZE, endereco_cliente)
                
                # Se o GetArquiveData terminou, significa que o ficheiro foi recebido com sucesso. Sai do While.
                break

            except socket.timeout: 
                # Se esgotar o tempo, volta a tentar receber
                continue
                 
        print(f"[CLIENTE] O ficheiro voltou e foi salvo como: '{nome_guardado}'\n")

    # Fecha o socket apenas quando todos os ficheiros do loop 'for' tiverem sido enviados e recebidos
    udp.close()

if __name__ == "__main__":
    iniciar_cliente()
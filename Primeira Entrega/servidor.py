# ==================================================
# IMPLEMENTAÇÃO DO SERVIDOR
# ==================================================

import socket

HOST = '127.0.0.1'      # IP do Servidor
PORT = 1044             # Porta onde o servidor vai "escutar" 
BUFFER_SIZE = 1024

def iniciar_servidor():
    # Cria o socket do servidor
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    udp.bind((HOST, PORT))
    print(f"[SERVIDOR] Servidor UDP rodando em {HOST}:{PORT}...\n")

    while True:
        try:
            print("[SERVIDOR] Aguardando recebimento de arquivo...")
            
            # Recebe o nome/extensão do arquivo
            msg_nome, endereco_cliente = udp.recvfrom(BUFFER_SIZE)
            nome_arquivo = msg_nome.decode('utf-8')
            
            # Nome que o servidor vai salvar o arquivo localmente
            nome_arquivo_servidor = f"servidor_{nome_arquivo}"
            print(f"[SERVIDOR] Nome do arquivo recebido: {nome_arquivo} de {endereco_cliente}")

            # Recebe e salva o conteúdo do arquivo
            with open(nome_arquivo_servidor, 'wb') as f:
                while True:
                    dados, _ = udp.recvfrom(BUFFER_SIZE)
                    
                    # Se receber um pacote vazio (b''), significa que é o fim do arquivo
                    if not dados:
                        print("[SERVIDOR] Fim do arquivo recebido pelo cliente.")
                        break
                    
                    f.write(dados) # Escreve a "parte" no arquivo salvo
            
            print(f"[SERVIDOR] Arquivo '{nome_arquivo_servidor}' salvo com sucesso!")

            # Devolve o arquivo p/ o cliente
            print("[SERVIDOR] Iniciando a devolução do arquivo para o cliente...")
            
            # Diz ao cliente o nome do arquivo que está voltando
            udp.sendto(nome_arquivo.encode('utf-8'), endereco_cliente)

            # Abre o arquivo recém-salvo
            with open(nome_arquivo_servidor, 'rb') as f:
                parte = f.read(BUFFER_SIZE)
                while parte:
                    udp.sendto(parte, endereco_cliente)
                    parte = f.read(BUFFER_SIZE) # Lê a próxima parte
                
                # Envia um pacote vazio para avisar ao cliente que o envio terminou
                udp.sendto(b'', endereco_cliente)
            
            print("[SERVIDOR] Arquivo devolvido com sucesso!\n")

        except KeyboardInterrupt:
            print("\n[SERVIDOR] Servidor encerrado pelo usuário.")
            break

    # Fecha a conexão ao sair do loop
    udp.close()

if __name__ == "__main__":
    iniciar_servidor()
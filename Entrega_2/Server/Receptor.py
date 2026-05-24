import socket
NUM_SEQUENCE = 0


def GetArquiveName(udp, B_msg, endereco_cliente, user, type):
    global NUM_SEQUENCE

    dados_msg = B_msg.decode('utf-8')
    num_sequence, data = dados_msg.split('|')

    if(int(num_sequence) == NUM_SEQUENCE):
        nome_arquivo = data
        

        # Nome que o servidor vai salvar o arquivo localmente
        nome_guardado = f"{type}_{nome_arquivo}"
        print(f"[{user}] Recebendo Arquivo: {nome_arquivo}")


        ack_msg = f"ACK{NUM_SEQUENCE}".encode('utf-8')
        udp.sendto(ack_msg, endereco_cliente)
        NUM_SEQUENCE = 1 if NUM_SEQUENCE == 0 else 0
        return 1, nome_guardado, nome_arquivo
    else:
        ack_msg = f"ACK{1 if NUM_SEQUENCE == 0 else 0}".encode('utf-8')
        udp.sendto(ack_msg, endereco_cliente)
        return 0
    
def GetArquiveData(udp, nome_guardado, BUFFER_SIZE, endereco_cliente ):
    global NUM_SEQUENCE

    with open(nome_guardado, 'wb') as f:
        while True:
            try:
                dados_msg, _ = udp.recvfrom(BUFFER_SIZE)
            except socket.timeout: continue

            separador = dados_msg.find(b'|')
            
            num_sequence = int(dados_msg[:separador].decode('utf-8'))
            data = dados_msg[separador + 1:]

            if data == b'FIM':
                if num_sequence == NUM_SEQUENCE:
                    # É o FIM que estávamos esperando. Manda o ACK e encerra!
                    ack_msg = f"ACK{NUM_SEQUENCE}".encode('utf-8')
                    udp.sendto(ack_msg, endereco_cliente)
                    
                    NUM_SEQUENCE = 1 if NUM_SEQUENCE == 0 else 0
                    break 
                else:
                    # É um FIM atrasado/duplicado. Reenvia o ACK antigo e continua.
                    ack_msg = f"ACK{1 if NUM_SEQUENCE == 0 else 0}".encode('utf-8')
                    udp.sendto(ack_msg, endereco_cliente)
                    continue
            

            if(num_sequence == NUM_SEQUENCE):
                f.write(data) # Escreve a "parte" no arquivo salvo

                ack_msg = f"ACK{NUM_SEQUENCE}".encode('utf-8')
                udp.sendto(ack_msg, endereco_cliente)

                NUM_SEQUENCE = 1 if NUM_SEQUENCE == 0 else 0

            else:
                ack_msg = f"ACK{1 if NUM_SEQUENCE == 0 else 0}".encode('utf-8')
                udp.sendto(ack_msg, endereco_cliente)
                continue
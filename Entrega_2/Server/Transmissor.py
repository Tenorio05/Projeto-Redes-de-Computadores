import socket, os
NUM_SEQUENCE = 0

def SendArquive(data, endereco_cliente, BUFFER_SIZE, udp):
    global NUM_SEQUENCE

    sequence = f'{NUM_SEQUENCE}|'.encode('utf-8')
    B_msg = sequence + data

    # 1. Envia o pacote pela PRIMEIRA vez (fora do loop de escuta)
    udp.sendto(B_msg, endereco_cliente)
    print(f"[Server T] Pacote {NUM_SEQUENCE} enviado. Aguardando ACK...")

    while True:
        try:
            # 2. Fica travado esperando a resposta (ACK) do receptor
            dados_ack, _ = udp.recvfrom(BUFFER_SIZE)
            ack_texto = dados_ack.decode('utf-8') 
            
            # Verifica se o ACK recebido é o que estávamos esperando
            if ack_texto == f"ACK{NUM_SEQUENCE}":
                print(f"[Server T] {ack_texto} recebido com sucesso!")
                
                # Alterna o número de sequência para o PRÓXIMO pacote
                NUM_SEQUENCE = 1 if NUM_SEQUENCE == 0 else 0
                break # Pacote entregue, sai do loop!
            
            else:
                print(f"[Server T] ACK incorreto recebido ({ack_texto}). Ignorando...")
                # 3. IMPORTANTE: Volta para o recvfrom() em silêncio, sem reenviar os dados!
                continue 
                
        except socket.timeout:
            # 4. SÓ REENVIA SE O TEMPO ESTOURAR!
            print(f"[TIMEOUT] O tempo esgotou! Retransmitindo pacote {NUM_SEQUENCE}...")
            udp.sendto(B_msg, endereco_cliente)
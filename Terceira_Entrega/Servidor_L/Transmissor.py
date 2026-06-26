import socket

# Sequência por cliente: endereco -> seq a usar no próximo envio
# Necessário para suportar múltiplos clientes simultaneamente sem conflito
# de número de sequência entre conversas independentes.
send_seq = {}

def SendArquive(data, endereco_cliente, BUFFER_SIZE, udp):
    global send_seq

    seq = send_seq.get(endereco_cliente, 0)

    sequence = f'{seq}|'.encode('utf-8')
    B_msg = sequence + data

    udp.sendto(B_msg, endereco_cliente)

    while True:
        try:
            dados_ack, _ = udp.recvfrom(BUFFER_SIZE)
            ack_texto = dados_ack.decode('utf-8')

            if ack_texto == f"ACK{seq}":
                send_seq[endereco_cliente] = 1 if seq == 0 else 0
                break
            else:
                # ACK de outro seq (ou de outro cliente): ignora e aguarda
                continue

        except socket.timeout:
            # Timeout: retransmite o mesmo pacote
            udp.sendto(B_msg, endereco_cliente)

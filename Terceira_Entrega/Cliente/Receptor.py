import socket

# Variável global para saber qual pacote o receptor está esperando
NUM_SEQUENCE = 0

def GetMsg(udp, B_msg, endereco_cliente):
    global NUM_SEQUENCE

    # Decodifica o pacote recebido
    dados_msg = B_msg.decode('utf-8')

    # Separa o número de sequência da mensagem usando o delimitador "|"
    num_sequence, data = dados_msg.split('|', 1)

    # Se o pacote for o esperado
    if int(num_sequence) == NUM_SEQUENCE:
        msg = data

        # ENVIA ACK: Confirma a recepção para o remetente
        ack_msg = f"ACK{NUM_SEQUENCE}".encode('utf-8')
        udp.sendto(ack_msg, endereco_cliente)

        # Prepara para esperar o próximo pacote
        NUM_SEQUENCE = 1 if NUM_SEQUENCE == 0 else 0

        return 1, msg

    else:
        # Pacote duplicado: reenvia o ACK antigo para desbloquear o remetente
        ack_msg = f"ACK{1 if NUM_SEQUENCE == 0 else 0}".encode('utf-8')
        udp.sendto(ack_msg, endereco_cliente)

        return 0, ""

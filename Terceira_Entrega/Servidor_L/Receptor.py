import socket

# Sequência por cliente: endereco -> seq esperado
# Com um único NUM_SEQUENCE global, o segundo cliente começa com seq=0
# mas o servidor já espera seq=1 (estado do primeiro cliente), rejeitando
# ou aceitando erroneamente todas as mensagens subsequentes.
recv_seq = {}

def GetMsg(udp, B_msg, endereco_cliente):
    global recv_seq

    dados_msg = B_msg.decode('utf-8')
    num_sequence, data = dados_msg.split('|', 1)

    expected = recv_seq.get(endereco_cliente, 0)

    if int(num_sequence) == expected:
        msg = data

        ack_msg = f"ACK{expected}".encode('utf-8')
        udp.sendto(ack_msg, endereco_cliente)

        recv_seq[endereco_cliente] = 1 if expected == 0 else 0

        return 1, msg

    else:
        # Pacote duplicado: reenvia o ACK anterior para desbloquear o remetente
        ack_msg = f"ACK{1 if expected == 0 else 0}".encode('utf-8')
        udp.sendto(ack_msg, endereco_cliente)

        return 0, ""

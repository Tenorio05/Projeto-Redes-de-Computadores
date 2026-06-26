import socket

# Variável global para gerir o Stop-and-Wait (Sempre 0 ou 1)
NUM_SEQUENCE = 0

def SendArquive(data, endereco_cliente, BUFFER_SIZE, udp):
    global NUM_SEQUENCE

    # CABEÇALHO: Adiciona o número de sequência seguido de um delimitador "|" antes dos dados
    sequence = f'{NUM_SEQUENCE}|'.encode('utf-8')
    B_msg = sequence + data

    # 1. ENVIO INICIAL: Envia o pacote de dados
    udp.sendto(B_msg, endereco_cliente)

    # Loop de Stop-and-Wait
    while True:
        try:
            # 2. ESPERA: Fica travado a ouvir a rede à espera do ACK correspondente
            dados_ack, _ = udp.recvfrom(BUFFER_SIZE)
            ack_texto = dados_ack.decode('utf-8')

            # 3. VALIDAÇÃO: Verifica se o ACK recebido é o correto
            if ack_texto == f"ACK{NUM_SEQUENCE}":
                # Sucesso! Troca o número de sequência para o próximo envio
                NUM_SEQUENCE = 1 if NUM_SEQUENCE == 0 else 0
                break

            else:
                # Recebeu um ACK antigo. Apenas ignora.
                continue

        except socket.timeout:
            # 4. TIMEOUT: Retransmite o MESMO pacote
            udp.sendto(B_msg, endereco_cliente)

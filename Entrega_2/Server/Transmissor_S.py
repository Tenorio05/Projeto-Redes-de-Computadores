import socket, os

# Variável global para gerir o Stop-and-Wait (Sempre 0 ou 1)
NUM_SEQUENCE = 0

def SendArquive(data, endereco_cliente, BUFFER_SIZE, udp):
    global NUM_SEQUENCE

    # CABEÇALHO: Adiciona o número de sequência seguido de um delimitador "|" antes dos dados
    sequence = f'{NUM_SEQUENCE}|'.encode('utf-8')
    B_msg = sequence + data

    # 1. ENVIO INICIAL: Envia o pacote de dados e avisa o terminal
    udp.sendto(B_msg, endereco_cliente)
    print(f"[T] Pacote {NUM_SEQUENCE} enviado. Aguardando ACK...")

    # Loop de Stop-and-Wait
    while True:
        try:
            # 2. ESPERA: Fica travado a ouvir a rede à espera do ACK correspondente
            dados_ack, _ = udp.recvfrom(BUFFER_SIZE)
            ack_texto = dados_ack.decode('utf-8') 
            
            # 3. VALIDAÇÃO: Verifica se o ACK recebido é o correto (Ex: Esperava ACK0 e chegou ACK0)
            if ack_texto == f"ACK{NUM_SEQUENCE}":
                print(f"[T] {ack_texto} recebido com sucesso!")
                
                # Sucesso! Troca o número de sequência (se for 0 vira 1, se for 1 vira 0) para o próximo envio
                NUM_SEQUENCE = 1 if NUM_SEQUENCE == 0 else 0
                break # Quebra o loop para poder enviar o pacote seguinte
            
            else:
                # Recebeu um ACK antigo (Ex: Esperava ACK1 mas chegou ACK0). Apenas ignora.
                print(f"[T] ACK incorreto recebido ({ack_texto}). Ignorando...")
                continue 
                
        except socket.timeout:
            # 4. TIMEOUT: Se passar 2 segundos e nenhum ACK chegar, assume que o pacote se perdeu na rede.
            # Retransmite o MESMO pacote imediatamente.
            print(f"[TIMEOUT] O tempo esgotou! Retransmitindo o pacote {NUM_SEQUENCE}...")
            udp.sendto(B_msg, endereco_cliente)
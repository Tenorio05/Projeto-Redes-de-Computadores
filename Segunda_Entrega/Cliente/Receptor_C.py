import socket

# Variável global para saber qual pacote o recetor está à espera
NUM_SEQUENCE = 0

def GetArquiveName(udp, B_msg, endereco_cliente, user, type):
    global NUM_SEQUENCE

    # Descodifica o pacote recebido
    dados_msg = B_msg.decode('utf-8')
    
    # Separa o número de sequência da mensagem usando o delimitador "|"
    num_sequence, data = dados_msg.split('|')

    # Se o pacote for o esperado (Ex: Chegou 0 e esperava 0)
    if(int(num_sequence) == NUM_SEQUENCE):
        nome_arquivo = data
        
        # Cria o nome final com que o ficheiro será gravado (ex: "servidor_teste.txt")
        nome_guardado = f"{type}_{nome_arquivo}"
        print(f"[{user}] A receber o Ficheiro: {nome_arquivo}")

        # ENVIA ACK: Confirma a receção para o remetente
        ack_msg = f"ACK{NUM_SEQUENCE}".encode('utf-8')
        udp.sendto(ack_msg, endereco_cliente)
        
        # Prepara para esperar o próximo pacote
        NUM_SEQUENCE = 1 if NUM_SEQUENCE == 0 else 0
        
        # Retorna 1 (Sucesso)
        return 1, nome_guardado, nome_arquivo
        
    else:
        # Se for um pacote duplicado (Ex: Esperava 1 mas chegou o 0 de novo)
        # Envia o ACK antigo para avisar o remetente que o zero já chegou.
        ack_msg = f"ACK{1 if NUM_SEQUENCE == 0 else 0}".encode('utf-8')
        udp.sendto(ack_msg, endereco_cliente)
        
        # Retorna 0 para avisar o código principal que este pacote é lixo
        return 0
    

def GetArquiveData(udp, nome_guardado, BUFFER_SIZE, endereco_cliente):
    global NUM_SEQUENCE

    # Abre (ou cria) o ficheiro em modo de escrita binária ('wb')
    with open(nome_guardado, 'wb') as f:
        while True:
            try:
                # Recebe os dados da rede
                dados_msg, _ = udp.recvfrom(BUFFER_SIZE)
            except socket.timeout: 
                continue # Se der timeout a ouvir, volta a escutar

            # Localiza onde está o "|" para separar o cabeçalho dos bytes do ficheiro
            separador = dados_msg.find(b'|')
            
            # Extrai o cabeçalho
            num_sequence = int(dados_msg[:separador].decode('utf-8'))
            
            # Extrai os dados puros do ficheiro
            data = dados_msg[separador + 1:]

            # SE CHEGAR AO FIM:
            if data == b'FIM':
                if num_sequence == NUM_SEQUENCE:
                    # É o pacote FIM na ordem correta. Envia um ACK para fechar.
                    ack_msg = f"ACK{NUM_SEQUENCE}".encode('utf-8')
                    udp.sendto(ack_msg, endereco_cliente)
                    
                    # Reinicia a sequência para o próximo ficheiro
                    NUM_SEQUENCE = 1 if NUM_SEQUENCE == 0 else 0
                    break # Termina a receção do ficheiro
                else:
                    # É um FIM repetido que chegou fora de horas. Reenvia o ACK antigo.
                    ack_msg = f"ACK{1 if NUM_SEQUENCE == 0 else 0}".encode('utf-8')
                    udp.sendto(ack_msg, endereco_cliente)
                    continue
            
            # GRAVAÇÃO DOS DADOS: Se o pacote estiver na ordem correta
            if(num_sequence == NUM_SEQUENCE):
                # Escreve o pedaço de dados diretamente no disco rígido
                f.write(data)

                # Envia o ACK de confirmação
                ack_msg = f"ACK{NUM_SEQUENCE}".encode('utf-8')
                udp.sendto(ack_msg, endereco_cliente)

                # Alterna o estado da máquina para o próximo pacote
                NUM_SEQUENCE = 1 if NUM_SEQUENCE == 0 else 0
                
            else:
                # É um pacote de dados repetido. Não grava no disco, apenas reenvia o ACK antigo.
                ack_msg = f"ACK{1 if NUM_SEQUENCE == 0 else 0}".encode('utf-8')
                udp.sendto(ack_msg, endereco_cliente)
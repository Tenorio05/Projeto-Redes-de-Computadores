import socket
import os
import Receptor as Rcpt
import Print as Prt
import Dados_L as dtl

def WaitCall(udp):
    """Função bloqueante que escuta a rede aguardando pacotes de clientes."""
    # Fica aguardando receber dados brutos da rede UDP
    b_msg, endereço_comprador = udp.recvfrom(dtl.BUFFER_SIZE)
    
    # Passa pelo seu protocolo de recebimento (Stop-and-wait, checagem de erros)
    num, msg = Rcpt.GetMsg(udp, b_msg, endereço_comprador)
    
    # Se recebeu um pacote inválido ou duplicado, retorna 0
    if not num: return 0
    
    # Se for um pacote válido, repassa a mensagem para a lógica principal processar o comando
    dtl.Funcoes(msg, endereço_comprador, udp)
    return 1

def Licitante():
    """Loop principal que gerencia o ciclo de vida do servidor de leilão."""
    # Cria o socket do tipo UDP (SOCK_DGRAM) usando endereçamento IPv4 (AF_INET)
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Define o temporizador do socket. Se passar este tempo sem receber nada, dá TimeoutError
    udp.settimeout(dtl.TIMEOUT)

    # Liga o socket ao IP e à porta escolhida para começar a escutar
    udp.bind((dtl.HOST, dtl.PORT))

    print(f"===== SISTEMA DE LEILAO =====\n\n\n")
    
    # Loop infinito do servidor
    while True:
        try:
            # A máquina de estados do servidor, baseada na variável Operation
            match dtl.Operation:

                case "WAIT":
                    # MODO DE ESPERA: Aguarda jogadores entrarem e darem "ready"
                    
                    if len(dtl.arquivos) < 1:
                        # Se não há mais arquivos, avisa que o leilão acabou e encerra
                        Prt.msg("Nao ha itens para leilao\n" 
                                "Fim do leilao")

                        msg_fim = {"tipo": "text", "msg": "Fim do Leilao! Ate a proxima!"}
                        for i in list(dtl.Compradores):
                            dtl.SendTo(msg_fim, i, udp)
                            dtl.Disconnect(i, udp)
                        break # Quebra o while True, encerrando o servidor

                    # Atualiza a interface gráfica do servidor
                    Prt.msg(f"----- Processo de login -----\n"
                            f"Compradores conectados ao leilao: {len(dtl.Compradores)}\n"
                            f"Numero de compradores prontos: {dtl.R_num}"
                    )

                    # Tenta receber alguma mensagem (como login ou ready)
                    if not WaitCall(udp): continue

                    # O leilão só pode iniciar se houver pelo menos 2 pessoas conectadas
                    if len(dtl.Compradores) < 2: continue

                    # Verifica se TODOS os compradores conectados deram "ready" (status 1)
                    prontos = 1
                    for i in dtl.Compradores.values():
                        if i[1] == 0: # Encontrou alguém que não está pronto
                            prontos = 0
                            break
                    
                    # Se todos estiverem prontos, inicia a fase de lances
                    if prontos: dtl.Lances_init()

                case "LANCES":
                    # MODO DE LANCES: O leilão está rolando
                    
                    ultimo_lançador = dtl.arquivos[dtl.id_atual][2]
                    
                    # Atualiza o painel do servidor com o status em tempo real
                    Prt.msg(
                        f"----- Processo de lances -----\n"
                        f"Item em Leilao: {dtl.arquivos[dtl.id_atual][0]}\n"
                        f"Valor atual: {dtl.arquivos[dtl.id_atual][1]}\n"
                        f"Ultimo lancador: {ultimo_lançador if ultimo_lançador != 'ninguem' else 'ninguem'}\n"
                        f"Tempo decorrido: {dtl.time.time() - dtl.tempo_leilao}"
                    )
                    
                    # CRITÉRIOS DE PARADA: 60 segundos ou 5 lances realizados no item
                    if (dtl.time.time() - dtl.tempo_leilao >= 60) or dtl.num_lances >= 5:
                        dtl.FimDeLeilao(udp) # Executa rotina de finalização do item
                        continue

                    # Escuta lances. O timeout curto permite que o painel e os cronômetros continuem rodando
                    if not WaitCall(udp): continue

        # Exceção tratada para que o servidor não feche se ninguém enviar dados em 2 segundos
        except (socket.timeout, TimeoutError):
            continue

        # Encerra graciosamente se o administrador pressionar Ctrl+C no terminal do servidor
        except KeyboardInterrupt:
            print("\n[SERVIDOR] Servidor encerrado.")
            break

if __name__ == "__main__":
    Licitante()

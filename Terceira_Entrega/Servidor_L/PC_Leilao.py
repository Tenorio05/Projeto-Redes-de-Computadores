import socket
import os
import Receptor as Rcpt
import Print as Prt
import Dados_L as dtl



def WaitCall(udp):
    b_msg, endereço_comprador = udp.recvfrom(dtl.BUFFER_SIZE)
    num, msg = Rcpt.GetMsg(udp, b_msg, endereço_comprador)
    if not num: return 0
    dtl.Funcoes(msg, endereço_comprador, udp)
    return 1

def Licitante():
    
    # Cria o socket do tipo UDP (SOCK_DGRAM) usando endereçamento IPv4 (AF_INET)
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Define o temporizador do socket. Se passar este tempo sem receber nada, dá TimeoutError
    udp.settimeout(dtl.TIMEOUT)
    
    # Liga o socket ao IP e à porta escolhida para começar a escutar
    udp.bind((dtl.HOST, dtl.PORT))

    print(f"===== SISTEMA DE LEILAO =====\n\n\n")
    while True:
        try:
            match dtl.Operation:

                case "WAIT":
                    if len(dtl.arquivos) < 1:
                        print("Não há itens para leilao")

                        if len(dtl.Compradores) > 1:
                            msg = {"msg":"Fim do Leilao! Até a proxima!"}

                            for i in dtl.Compradores:
                                dtl.SendTo(msg, i, udp)
                                dtl.Disconnect(i, udp)
                        break 
                    
                    Prt.msg(f"----- Processo de login -----\n"
                            f"Compradores conectados ao leilao: {len(dtl.Compradores)}"
                    )

                    if not WaitCall(udp): continue
                    
                    if len(dtl.Compradores) < 2: continue

                    prontos = 1
                    for i in dtl.Compradores.values():
                        if i[1] == 0:
                            prontos = 0
                            break
                    if prontos: dtl.Lances_init()

                case "LANCES":

                    Prt.msg(
                        f"----- Processo de lances -----\n"
                        f"Item em Leilao: {dtl.arquivos[dtl.id_atual][0]}\n"
                        f"Valor atual: {dtl.arquivos[dtl.id_atual][1]}\n"
                        f"Ultimo lancador: {dtl.arquivos[dtl.id_atual][2] if dtl.arquivos[dtl.id_atual][2] != '1' else "ninguem"}"
                    )
                    if (dtl.time.time() - dtl.tempo_leilao >= 60) or dtl.num_lances == 5:
                        dtl.FimDeLeilao(udp)

                    if not WaitCall(udp): continue


        # Exceção tratada para que o servidor não feche se ninguém enviar arquivos em 2 segundos
        except (socket.timeout, TimeoutError):
            continue 

        # Encerra graciosamente se o utilizador pressionar Ctrl+C no terminal
        except KeyboardInterrupt:
            print("\n[SERVIDOR] Servidor encerrado.")
            break


if __name__ == "__main__":
    Licitante()

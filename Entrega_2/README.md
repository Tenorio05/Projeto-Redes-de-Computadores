# Projeto Fundamentos de Redes de Computadores - 2026.1
Temática: AuctionCIn - Sistema de Leilão Multi-Usuário
Etapa 2: Implementando uma transferência confiável com RDT 3.0

Integrantes da Equipe
- Theo William da Rocha Ferreira
- Thiago Tenório de Albuquerque
- Henrique Garcia Leite
- Antônio Eduardo Nery de Sousa

Descrição da Entrega
Segunda etapa do projeto AuctionCIn, onde o objetivo cumprido nesta fase é a simulação de uma transferência confiável utilizando o protocolo RDT 3.0 sobre uma comunicação UDP com a biblioteca nativa socket do Python.

A aplicação realiza o envio, armazenamento e devolução de múltiplos tipos de arquivos. Para testar a eficiência e confiabilidade do RDT 3.0, foi implementado um gerador de perdas de pacotes aleatórios. Ele força o timeout no recebimento, ativando as retransmissões (Stop-and-Wait com alternância de bits 0 e 1). Cada passo é exibido na linha de comando de modo a permitir a compreensão do que está acontecendo (envios, perdas, timeouts e ACKs). A implementação do checksum no RDT 3.0 não foi necessária, pois utilizou-se a verificação nativa do UDP e camada de enlace.

Pré-requisitos e Observações Importantes
Antes de executar os códigos, atente-se às seguintes configurações presentes nos scripts:

- Endereço IP:
Ambos os códigos estão configurados com o IP 'localhost', que funciona para teste em rede local (mesma máquina). Para testar em máquinas separadas, altere a variável de host nos códigos para o IP atual da máquina servidora.

- Arquivos Necessários:
O código do cliente foi estruturado para testar diferentes formatos. Para que ele funcione corretamente, os seguintes arquivos devem existir no diretório Cliente:
    - teste.txt
    - bianca-cel.jpg
    - AuctionCIn.pdf
    - nggyu.mp3
    - shaaaw.mp3
    - auramaisego.mp3

Instruções de Execução

Passo 1: Iniciar o Servidor
O servidor deve estar rodando antes de o cliente tentar enviar os arquivos. Abra um terminal de comando na pasta do projeto e abra a pasta \Server:
cd '.\Entrega_2\Server\'
python Server_2.py

Passo 2: Iniciar o Cliente
Abra um segundo terminal de comando na pasta do projeto e abra a pasta \Cliente:
cd '.\Entrega_2\Cliente\'
python Cliente_2.py

Passo 3: Verificação
Acompanhe os logs em ambos os terminais. O cliente informará o envio dos pacotes, os timers de timeout e as perdas propositais simuladas. O servidor confirmará o recebimento, o processamento de números de sequência esperados, o salvamento e a devolução. Ao final da execução com sucesso, será possível verificar nos logs do terminal a retransmissão de pacotes que simularam perda, confirmando a robustez do RDT 3.0.
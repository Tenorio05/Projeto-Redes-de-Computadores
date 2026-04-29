# Projeto Fundamentos de Redes de Computadores - 2026.1
**Temática:** AuctionCIn - Sistema de Leilão Multi-Usuário

**Etapa 1:** Transmissão de arquivos com UDP

## 👥 Integrantes da Equipe
* Theo William da Rocha Ferreira
* Thiago Tenório de Albuquerque
* Henrique Garcia Leite
* Antônio Eduardo Nery de Sousa

---

## 📌 Descrição da Entrega
Primeira etapa do projeto AuctionCIn, onde o objetivo cumprido nesta fase é a implementação de uma comunicação UDP utilizando a biblioteca nativa `socket` do Python. 

A aplicação realiza o envio de múltiplos arquivos do cliente para o servidor, particionando os dados em buffers de **1024 bytes**. O servidor recebe as partes, armazena o arquivo localmente com o prefixo `servidor_` e, em seguida, devolve o arquivo para o cliente com o prefixo `leilao_`, comprovando o tráfego de via dupla dos pacotes UDP.

---

## ⚠️ Pré-requisitos e Observações Importantes

Antes de executar os códigos, atente-se às seguintes configurações presentes nos scripts:

1. **Endereço IP:** 

    * Ambos os códigos (`_cliente.py` e `_servidor.py`) estão configurados com o IP `'localhost'`, que funciona para teste em rede local **(mesma máquina)**.
    * Para testar em **máquinas separadas**, altere a variável `HOST` em ambos os códigos para o IP atual da máquina servidora.

2. **Arquivos Necessários:**

   O arquivo `_cliente.py` foi programado para iterar e enviar uma lista específica de arquivos ao servidor para testar diferentes formatos. Para que ele funcione corretamente, os seguintes arquivos devem existir no mesmo diretório de `_cliente.py`:
   * `teste.txt`
   * `kurose.png`
   * `AuctionCIn.pdf`
   * `nggyu.mp3`
   * `shaaaw.mp3`
   * `auramaisego.mp3`
   
   *OBS:* Caso algum desses arquivos não seja encontrado, o código do cliente irá pulá-lo e seguirá com o envio dos arquivos subsequentes.

---

## 🚀 Instruções de Execução

### Passo 1: Iniciar o Servidor
O servidor deve estar rodando antes de o cliente tentar enviar os arquivos.
1. Abra um terminal de comando na pasta do projeto e abra a pasta ``\Server`` com o comando:
    
    ```bash
    cd '.\Primeira_Entrega\Server\'
2. Execute o script do servidor com o comando:
    ```bash
    python _servidor.py
O terminal exibirá a mensagem indicando que está aguardando conexões: [SERVIDOR] Servidor UDP rodando em 172.20.18.24:1044...

### Passo 2: Iniciar o Cliente
1. Abra um segundo terminal de comando na pasta do projeto e abra a pasta ``\Client`` com o comando:
    
    ```bash
    cd '.\Primeira_Entrega\Client\'
2. Execute o script do cliente com o comando:
    ``` bash
    python _cliente.py
3. Acompanhe os logs em ambos os terminais. O cliente informará o envio em blocos, e o servidor confirmará o recebimento, o salvamento e a devolução.

### Passo 3: Verificação
Ao final da execução com sucesso, a pasta ``\Client`` conterá:
* Os arquivos originais intactos, assim como as cópias devolvidas pelo servidor, nomeadas com o prefixo leilao_ (ex: leilao_teste.txt).

E a pasta ``\Server``:
* As cópias armazenadas pelo servidor, nomeadas com o prefixo servidor_ (ex: servidor_teste.txt).
# 🔨 AuctionCIn - Sistema de Leilão Multi-Usuário

**Disciplina:** Fundamentos de Redes de Computadores - 2026.1  
**Instituição:** Centro de Informática (CIn) - UFPE  
**Temática:** Sistema de Leilão Multi-Usuário com confiabilidade sobre UDP

---

## 👥 Equipe
* Thiago Tenório de Albuquerque - tta2
* Theo William da Rocha Ferreira - twrf
* Henrique Garcia Leite - hgl
* Antônio Eduardo Nery de Sousa - aens

---

## 📖 Sobre o Projeto
O **AuctionCIn** é um sistema de leilões online multiusuário desenvolvido inteiramente sobre o protocolo UDP. O projeto foi dividido em três etapas incrementais, focando na implementação de transmissão confiável de dados na camada de aplicação (utilizando RDT 3.0) e na gerência de estados concorrentes no servidor.

Este repositório contém a consolidação das três entregas do projeto.

---

## ⚙️ Pré-requisitos
* **Python 3.8+** instalado nativamente.
* Nenhuma biblioteca externa é necessária além das nativas (`socket`, `json`, `threading`, `time`, `os`).

---

## 🚀 Estrutura e Execução das Entregas

### 📦 1. Primeira Etapa: Transmissão de Arquivos com UDP
**Objetivo:** Estabelecer a comunicação base via sockets UDP com envio, armazenamento e devolução de arquivos fragmentados (buffer de 1024 bytes).
* **Execução:**
  ```bash
  # Inicie o servidor
  python Primeira_Entrega/Servidor/servidor.py
  # Inicie o cliente
  python Primeira_Entrega/Cliente/cliente.py
  ```

---

### 🛡️ 2. Segunda Etapa: Transferência Confiável com RDT 3.0
**Objetivo:** Evoluir a comunicação para um canal confiável implementando o **RDT 3.0** (Stop-and-Wait) na camada de aplicação.
* Inclui simulação de perda de pacotes, ACKs e timeout para retransmissão.
* **Execução:**
  ```bash
  # Inicie o servidor
  python Segunda_Entrega/Server/Servidor_2.py
  # Inicie o cliente
  python Segunda_Entrega/Cliente/Cliente_2.py
  ```

---

### 🛒 3. Terceira Etapa: Sistema AuctionCIn (Aplicação Final)
**Objetivo:** Sistema de leilão interativo no paradigma Cliente-Servidor com múltiplos clientes simultâneos, utilizando o RDT 3.0 subjacente.

* **Execução:**
  ```bash
  # Inicie o servidor do leilão
  python Terceira_Entrega/Servidor_L/PC_Leilao.py
  # Inicie os clientes (em terminais separados)
  python Terceira_Entrega/Cliente/Cliente.py
  ```

#### ⚠️ Notas Importantes de Uso (Fluxo Atual Implementado)
Devido a algumas decisões de arquitetura na implementação atual, atente-se ao seguinte fluxo para testar a aplicação corretamente:

1. **Login e Confirmação (`ready`):** 
   * Ao iniciar, o cliente deve usar `login <nome>`. 
   * O servidor responderá solicitando um sinal de prontidão. **Você deve digitar `ready`** no cliente para que o servidor saia do estado de espera e inicie o leilão.
2. **Fim do Leilão:** O servidor está programado para iterar sobre os itens pré-definidos (ex: Carro.txt, Moto.txt). Quando a lista de itens acaba, o servidor encerra as conexões.
3. **Comandos Suportados:**
   * `login <nome_do_usuario>`: Registra o usuário.
   * `ready`: Confirma prontidão para iniciar o leilão (Comando adicional da implementação).
   * `bid <id_item> <valor>`: Envia um lance.
   * `list`: Lista itens disponíveis.
   * `status`: Exibe quem está ganhando o item atual.
   * `logout`: Desconecta o usuário.

---

## 📌 Arquitetura e Modularização
O código foi refatorado para separar a lógica de rede da lógica de negócio:
* `Transmissor.py` / `Receptor.py`: Lidam com a complexidade do protocolo RDT 3.0 (empacotamento, ACKs, timeouts).
* `Dados_L.py` / `PC_Leilao.py`: Controlam as regras do leilão, temporizadores dos itens e broadcast de mensagens.

---
*Desenvolvido para a disciplina de Fundamentos de Redes de Computadores - UFPE (2026.1).*

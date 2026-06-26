# 🏷️ AuctionCin - Implementação do Cliente

## 📌 Objetivo

Este documento descreve o protocolo de comunicação utilizado pelo servidor do **AuctionCin**. O cliente deverá implementar apenas a interface do usuário e a comunicação com o servidor.

Toda a comunicação é feita via **UDP utilizando o protocolo RDT 3.0 (Stop-and-Wait)**, que já está implementado pelos módulos `Transmissor.py` e `Receptor.py`.

> ⚠️ **ATENÇÃO:** Nunca utilize `socket.sendto()` ou `recvfrom()` diretamente para enviar ou receber mensagens da aplicação com o servidor.

Sempre utilize as funções fornecidas:

* **Para enviar:** `Transmissor.SendArquive(...)`
* **Para receber:** `Receptor.GetMsg(...)`

---

## 📤 1. Comandos Enviados ao Servidor

Todas as mensagens enviadas ao servidor são **strings**, separadas pelo caractere `#`.

**Formato geral:**

```text
<comando>#<argumento1>#<argumento2>#...

```

### 👤 Login

```text
login#Theo

```

O servidor interpreta o comando `login` e o nome do usuário (`Theo`).

### ✅ Confirmar Prontidão

```text
ready

```

Não exige argumentos.

### 💰 Dar Lance

```text
bid#<id_item>#<valor>

```

* **Exemplo:** `bid#2#1520.50`
* O valor deve ser enviado como texto. O servidor converte automaticamente para `float`.

### 📜 Listar Itens

```text
list

```

Não exige argumentos.

### 🏆 Ver Vencedor Atual

```text
status

```

Não exige argumentos.

### 🚪 Logout

```text
logout

```

Não exige argumentos.

---

## 📥 2. Formato das Respostas do Servidor

Toda resposta do servidor é enviada no formato **JSON**. Após receber um pacote, você deve decodificá-lo:

```python
dados = json.loads(msg)

```

Sempre verifique o campo `"tipo"`. Esse campo define como interpretar o restante da mensagem recebida.

---

## 🗂️ 3. Tipos de Mensagens do Servidor

### 🔹 Tipo 1: Texto Simples (`text`)

Mensagem simples para ser exibida ao usuário.

**Formato:**

```json
{
    "tipo": "text",
    "msg": "Você está online."
}

```

**O que o cliente deve fazer:** Apenas imprimir o conteúdo de `msg`. Outros exemplos de mensagens incluem "Confirmado!", "Erro." e "Desconectado.".

### 🔹 Tipo 2: Texto com Dados (`text&dado`)

O cliente deve primeiro imprimir a `msg` e, em seguida, interpretar o `dado` dependendo do contexto da operação.

**Formato Genérico:**

```json
{
    "tipo": "text&dado",
    "msg": "...",
    "dado": "..."
}

```

**Contextos do `dado`:**

**A. Novo Lance:**

* **Formato do dado:** Lista contendo `[valor, comprador]`.
* **Ação:** Atualizar a interface exibindo o valor atual e o comprador líder.

**B. Listagem de Itens:**

* **Formato do dado:** Dicionário onde a chave é o `id_item` e o valor é `[nome_do_arquivo, valor_atual]`. Exemplo: `"1": ["Carro.txt", 1000]`.
* **Ação:** Percorrer todo o dicionário e imprimir os itens disponíveis.

**C. Status do Vencedor:**

* **Formato do dado:** String com o nome de quem está vencendo. Exemplo: `"Theo"`.
* **Ação:** Apenas imprimir o nome recebido.

---

## 📦 4. Recebimento do Arquivo do Vencedor

Quando o usuário vencer um leilão, o servidor enviará o arquivo do prêmio em vários blocos.

**Formato do Bloco:**

```json
{
    "tipo": "text&arquivo",
    "msg": "Parabéns!",
    "nome": "Carro.txt",
    "dados": "<base64>"
}

```

### Decodificando e Salvando os Dados

O campo `"nome"` indica o nome que o arquivo deverá possuir ao ser salvo. O campo `"dados"` contém um bloco do arquivo convertido para **Base64**. O cliente deverá converter novamente para bytes antes de salvar:

```python
import base64

dados = base64.b64decode(msg["dados"])

```

### Gravação no Disco

O arquivo deve ser aberto obrigatoriamente no modo `ab` (*append binary*):

```python
with open(msg["nome"], "ab") as f:
    f.write(dados)

```

> ⚠️ **ATENÇÃO:** Nunca utilize o modo `wb` durante o recebimento dos blocos, pois isso apagará os dados dos blocos recebidos anteriormente.

---

## 🏁 5. Fim da Transferência de Arquivo

Após o envio do último bloco, o servidor enviará uma mensagem indicando o término da transferência.

**Formato:**

```json
{
    "tipo": "fim_arquivo"
}

```

**Ao receber esta mensagem, o cliente deverá:**

1. Fechar o arquivo (caso ainda esteja aberto).
2. Informar ao usuário que o item foi recebido com sucesso.
3. Voltar ao modo normal de operação.

---

## 🔄 6. Atualizações Automáticas (Assíncronas)

Mesmo que o usuário não execute nenhum comando, o servidor poderá enviar mensagens espontaneamente a qualquer momento. Isso garante que todos os participantes permaneçam sincronizados com o estado do leilão.

**Exemplos de eventos assíncronos:**

* Novo lance realizado por outro comprador.
* Encerramento do leilão.
* Início do envio do prêmio.

**Regra de Ouro:** O cliente deve permanecer **continuamente aguardando mensagens** do servidor para manter a interface atualizada, independentemente de ter enviado um comando imediatamente antes.

---

## 📋 7. Resumo do Protocolo

### Cliente Envia

| Ação | Formato de Envio |
| --- | --- |
| **Login** | `login#nome` |
| **Pronto** | `ready` |
| **Lance** | `bid#id#valor` |
| **Lista** | `list` |
| **Status** | `status` |
| **Logout** | `logout` |

### Servidor Responde

| Tipo JSON | Ação do Cliente |
| --- | --- |
| `text` | Imprimir o conteúdo de `msg`. |
| `text&dado` | Imprimir `msg` e interpretar a estrutura do `dado`. |
| `text&arquivo` | Decodificar os dados em Base64 e gravar no arquivo usando o modo `"ab"`. |
| `fim_arquivo` | Finalizar a gravação do arquivo e informar sucesso ao usuário. |

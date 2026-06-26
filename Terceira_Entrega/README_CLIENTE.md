Claro. Eu faria um README voltado para quem vai implementar apenas o **cliente**, explicando o protocolo de comunicação entre cliente e servidor. Assim a outra pessoa não precisa ler o código do servidor para saber como se comunicar.

---

# README - Implementação do Cliente (AuctionCin)

## Objetivo

Este documento descreve o protocolo de comunicação utilizado pelo servidor do AuctionCin.

O cliente deverá implementar apenas a interface do usuário e a comunicação com o servidor. Toda comunicação é feita via **UDP utilizando o protocolo RDT 3.0**, já implementado pelos módulos `Transmissor.py` e `Receptor.py`.

**Nunca utilizar `socket.sendto()` diretamente para enviar mensagens ao servidor.**

Sempre utilizar:

```python
Transmissor.SendArquive(...)
```

e receber utilizando:

```python
Receptor.GetMsg(...)
```

---

# 1. Formato dos comandos enviados ao servidor

Todas as mensagens enviadas ao servidor são **strings**, separadas pelo caractere `#`.

Formato geral:

```
<comando>#<argumento1>#<argumento2>#...
```

## Login

```
login#Theo
```

Servidor interpreta:

```
login
nome = Theo
```

---

## Confirmar prontidão

```
ready
```

Sem argumentos.

---

## Dar lance

Formato:

```
bid#<id_item>#<valor>
```

Exemplo:

```
bid#2#1520.50
```

O valor deve ser enviado como texto.

O servidor converte para `float`.

---

## Listar itens

```
list
```

Sem argumentos.

---

## Ver vencedor atual

```
status
```

Sem argumentos.

---

## Logout

```
logout
```

Sem argumentos.

---

# 2. Formato das respostas do servidor

Toda resposta do servidor é enviada em **JSON**.

Após receber um pacote:

```python
dados = json.loads(msg)
```

Sempre verificar o campo:

```
tipo
```

Esse campo define como interpretar o restante da mensagem.

---

# 3. Tipos de mensagens

Atualmente existem três tipos.

---

## Tipo 1

```
tipo = "text"
```

Formato:

```json
{
    "tipo":"text",
    "msg":"..."
}
```

Utilização:

Mensagem simples ao usuário.

Exemplos:

```
Você está online.

Confirmado!

Erro.

Desconectado.
```

O cliente apenas imprime:

```
msg
```

---

## Tipo 2

```
tipo = "text&dado"
```

Formato:

```json
{
    "tipo":"text&dado",
    "msg":"...",
    "dado":...
}
```

Primeiro imprimir

```
msg
```

Depois interpretar

```
dado
```

dependendo da operação.

---

### Novo lance

```
{
    "tipo":"text&dado",
    "msg":"Novo lance!",
    "dado":[valor, comprador]
}
```

Atualizar a interface exibindo:

* valor atual
* comprador líder

---

### Listagem de itens

```
{
    "tipo":"text&dado",
    "msg":"Itens disponíveis",
    "dado":{
        "1":["Carro.txt",1000],
        "2":["Moto.txt",500]
    }
}
```

Cada item do dicionário representa:

```
id_item

↓

[nome_do_arquivo, valor_atual]
```

O cliente deve percorrer todo o dicionário e imprimir os itens.

---

### Status

```
{
    "tipo":"text&dado",
    "msg":"Quem está vencendo",
    "dado":"Theo"
}
```

Basta imprimir:

```
Theo
```

---

# 4. Recebimento do arquivo do vencedor

Quando o usuário vencer um leilão, o servidor enviará o arquivo em vários blocos.

Cada bloco possui o formato:

```json
{
    "tipo":"text&arquivo",
    "msg":"Parabéns!",
    "nome":"Carro.txt",
    "dados":"<base64>"
}
```

---

## Campo "nome"

Indica o nome que o arquivo deverá possuir ao ser salvo.

Exemplo:

```
Carro.txt
```

---

## Campo "dados"

Contém um bloco do arquivo convertido para Base64.

O cliente deverá converter novamente para bytes:

```python
import base64

dados = base64.b64decode(msg["dados"])
```

---

## Salvando o arquivo

O arquivo deve ser aberto utilizando

```python
with open(msg["nome"], "ab") as f:
```

Modo

```
ab
```

significa

```
append binary
```

Cada bloco recebido deverá ser escrito utilizando

```python
f.write(dados)
```

Nunca utilizar

```
wb
```

durante o recebimento dos blocos, pois isso apagaria os dados já recebidos.

---

# 5. Fim do arquivo

Após o envio do último bloco, o servidor deverá enviar uma mensagem indicando o término da transferência.

Formato esperado:

```json
{
    "tipo":"fim_arquivo"
}
```

Ao receber esta mensagem, o cliente deverá:

* fechar o arquivo (caso ainda esteja aberto);
* informar ao usuário que o item foi recebido com sucesso;
* voltar ao modo normal de operação.

---

# 6. Atualizações automáticas

Mesmo que o usuário não execute nenhum comando, o servidor poderá enviar mensagens espontaneamente.

Exemplos:

* novo lance realizado por outro comprador;
* encerramento do leilão;
* início do envio do prêmio.

O cliente deve permanecer continuamente aguardando mensagens do servidor para manter a interface atualizada.

---

# 7. Resumo do protocolo

| Cliente envia | Formato        |
| ------------- | -------------- |
| Login         | `login#nome`   |
| Pronto        | `ready`        |
| Lance         | `bid#id#valor` |
| Lista         | `list`         |
| Status        | `status`       |
| Logout        | `logout`       |

---

| Servidor responde | Tipo           | Ação do cliente                       |
| ----------------- | -------------- | ------------------------------------- |
| Texto simples     | `text`         | imprimir `msg`                        |
| Texto + dados     | `text&dado`    | imprimir `msg` e interpretar `dado`   |
| Bloco de arquivo  | `text&arquivo` | decodificar Base64 e gravar em `"ab"` |
| Fim do arquivo    | `fim_arquivo`  | finalizar gravação e informar sucesso |

---

## Observações

* Toda comunicação utiliza **RDT 3.0 (Stop-and-Wait)**. O cliente não deve utilizar diretamente `sendto()` ou `recvfrom()` para trocar mensagens da aplicação, mas sim as funções fornecidas nos módulos `Transmissor.py` e `Receptor.py`.
* Os comandos enviados ao servidor são sempre strings no formato `comando#argumentos`.
* Todas as respostas do servidor são objetos JSON e devem ser interpretadas de acordo com o campo `tipo`.
* O cliente deve estar preparado para receber mensagens assíncronas (como novos lances ou o encerramento de um leilão), independentemente de ter enviado um comando imediatamente antes. Isso garante que todos os participantes permaneçam sincronizados com o estado do leilão.

# Envio automatizado de notificação individual (dengue/chikungunya) ao SINAN

Scripts em Python que preenchem a **parte de notificação** da ficha individual de
dengue/chikungunya no SINAN (sinan.saude.gov.br) usando o mesmo mecanismo AJAX da
tela, e uma ferramenta para descobrir o **código de bairro** do SINAN.

> **Atenção:** o envio cria uma **notificação real** no SINAN. Sempre rode
> `--simular` antes e confira com a vigilância se a ficha ainda não foi digitada
> e se o número da notificação está reservado para ela.

## Conteúdo

| Arquivo | Para que serve |
|---|---|
| `src/api/sinan/client.py` | Autentica, executa os eventos AJAX e envia a ficha (ou só simula com `--simular`). |
| `src/api/sinan/sinan_extrair_bairros.py` | Varre os códigos de bairro do município e grava em CSV; também busca no CSV. |
| `dados/bairros_sinan_ids.csv` | Tabela já extraída de Dourados/MS (IDs 1 a 650, 564 bairros), em `ID;NM_BAIRRO;CATEGORIA`. |
| `dados/ficha_modelo.json` | Modelo de ficha para copiar e preencher. |
| `dados/campos_selecao_sinan.xlsx` | Mapeamento dos campos e opções do formulário do SINAN (referência). |
| `instalar.ps1` | Cria o `.venv` e instala as dependências. |
| `configurar_credenciais.ps1` | Grava usuário/senha do SINAN como variáveis de ambiente, com senha oculta. |
| `relatorios/` | Onde ficam os resultados de cada envio. |

## Instalação (uma vez)

Requer Windows, Python 3.10+ e acesso ao SINAN.

```powershell
powershell -ExecutionPolicy Bypass -File .\instalar.ps1
powershell -ExecutionPolicy Bypass -File .\configurar_credenciais.ps1
```

Feche e abra o terminal depois de configurar as credenciais. Os scripts leem
**somente** as variáveis `SINAN_USERNAME` e `SINAN_PASSWORD`. Nunca coloque usuário
ou senha dentro do código.

## Passo a passo para enviar uma ficha

### 1. Criar a ficha

Copie `dados/ficha_modelo.json` para `dados/ficha_<NUMERO>.json` e substitua todos
os `PREENCHER`. O script recusa a ficha se sobrar algum `PREENCHER`.

| Chave | Formato / exemplo |
|---|---|
| `numero_notificacao` | número reservado, ex.: `"3331701"` |
| `agravo` | `"A92.0 - FEBRE DE CHIKUNGUNYA"` ou `"A90 - DENGUE"` (texto exato do SINAN) |
| `data_notificacao`, `data_primeiros_sintomas`, `data_nascimento` | `"dd/mm/aaaa"` |
| `mes_referencia` | mês da notificação, `"mm/aaaa"` |
| `semana_notificacao`, `semana_primeiros_sintomas` | `"aaaass"`, ex.: `"202639"` (o SINAN recalcula pelas datas) |
| `cnes` / `unidade_saude` | CNES e nome exato da unidade no SINAN |
| `idade` + `tipo_idade` | ex.: `"35"` + `"4"` (anos) |
| `bairro_id` / `bairro` | ver passo 2 |
| `logradouro`, `numero_residencia` | texto livre |

Tabela de códigos:

- **tipo_idade:** 1 = hora, 2 = dia, 3 = mês, 4 = ano
- **sexo:** M = masculino, F = feminino, I = ignorado
- **gestante:** 1, 2 ou 3 = 1º, 2º ou 3º trimestre; 4 = idade gestacional ignorada; 5 = não; **6 = não se aplica**; 9 = ignorado
- **raca:** 1 = branca, 2 = preta, 3 = amarela, 4 = parda, 5 = indígena, 9 = ignorado
- **escolaridade:** 0 = analfabeto; 1 = 1ª a 4ª série incompleta do EF; 2 = 4ª série completa do EF; 3 = 5ª a 8ª série incompleta do EF; 4 = EF completo; 5 = EM incompleto; 6 = EM completo; 7 = superior incompleto; 8 = superior completo; 9 = ignorado; 10 = não se aplica
- **zona:** 1 = urbana, 2 = rural, 3 = periurbana, 9 = ignorado
- **UF:** MS = `12`. **Município:** código IBGE de 6 dígitos (Dourados = `500370`)

### 2. Descobrir o código do bairro

Busque na tabela já extraída. Isso **não precisa de login**: com `--inicio`
maior que `--fim`, nada é consultado no SINAN.

```powershell
.\.venv\Scripts\python.exe .\src\sinan_extrair_bairros.py --inicio 1 --fim 0 --buscar "RASSELEM"
```

Preencha na ficha:
- `bairro_id`: o ID, só dígitos, ex.: `"391"`
- `bairro`: o texto **exato** da coluna `NM_BAIRRO`, ex.: `"JD MANOEL RASSELEM - BAIRRO"`

O bairro no SINAN é um campo aberto, então **o mesmo bairro pode aparecer mais de
uma vez** (ex.: SIRIA RASSELEM nos IDs 393 e 468, SIRYA RASSELEN CCZ no 215). Na
dúvida, confirme com a vigilância qual ID usar. Se a categoria do bairro não for
`BAIRRO` (ex.: `FAZENDA`), avise antes de enviar: hoje o script envia a categoria
`BAIRRO` fixa.

Para atualizar a tabela ou extrair outro município (consulta só leitura, não salva nada):

```powershell
# Dourados (padrão), retomando de onde parou
.\.venv\Scripts\python.exe .\src\sinan_extrair_bairros.py --inicio 1 --fim 700

# Outro município
.\.venv\Scripts\python.exe .\src\sinan_extrair_bairros.py --uf-id 12 --municipio-id 500270 --municipio-nome "CAMPO GRANDE" --arquivo .\dados\bairros_campo_grande.csv --fim 1500
```

Se o CSV já existir, os IDs já gravados são pulados. O script grava a cada 25 IDs
e reautentica uma vez se a sessão expirar.

### 3. Simular (obrigatório antes de enviar)

```powershell
.\.venv\Scripts\python.exe .\src\sinan_enviar_ficha.py --arquivo-ficha .\dados\ficha_3331701.json --simular
```

A simulação faz o login e todos os eventos AJAX, mas **não faz o POST final**.
Confira na saída:
- `Eventos AJAX executados: 9/9`
- `semana_devolvida[...]`: a semana calculada pelo SINAN
- `unidade_devolvida_cnes` igual a `Unidade no JSON`
- `bairro_devolvido` igual ao `bairro` da ficha e `categoria_devolvida`

Se algo divergir, corrija a ficha e simule de novo.

### 4. Enviar (uma única vez)

```powershell
.\.venv\Scripts\python.exe .\src\sinan_enviar_ficha.py --arquivo-ficha .\dados\ficha_3331701.json --confirmar-numero 3331701
```

- O `--confirmar-numero` precisa ser igual ao `numero_notificacao` da ficha.
- **Não repita o comando em caso de erro.** Primeiro verifique no SINAN se a ficha
  entrou, para não duplicar.
- O resultado fica em `relatorios/resultado_envio_ficha_<NUMERO>.json`.
  `CADASTRO_CONFIRMADO` significa que o SINAN respondeu "Operação realizada com
  sucesso". `RESPOSTA_REQUER_ANALISE` exige conferência manual.

### 5. Depois do envio

1. Abra a ficha no SINAN e confira: semanas, código e nome do bairro, categoria,
   agravo, gestante e unidade de saúde.
2. Complete manualmente o que o script não preenche: **CNS, CEP, telefone e toda a
   investigação (campos 31 em diante)**.
3. **Apague o arquivo `dados/ficha_<NUMERO>.json`**, porque ele contém dados do paciente.

## Regras de segurança

- Nunca compartilhe, versione nem envie por e-mail ou chat os arquivos `dados/ficha_*.json`
  nem os relatórios. O `.gitignore` já exclui esses arquivos.
- Não imprima nem grave senha, cookies ou ViewState em logs.
- O extrator de bairros só dispara eventos AJAX de **consulta**. Ele nunca clica em
  Ok/Salvar (há uma checagem no código que impede enviar `form:botaoOk`).
- Use `--simular` sempre que mudar algo no script ou na ficha.

## Como funciona (resumo técnico)

O SINAN usa JSF/RichFaces: o estado da tela fica no servidor (`javax.faces.ViewState`)
e cada campo dispara um `A4J.AJAX.Submit`. O script reproduz, em ordem, os eventos
que a tela dispara quando uma pessoa digita:

1. data de notificação e data dos primeiros sintomas (o servidor calcula as semanas;
   o evento da data de notificação fica no `onchanged` do calendário);
2. UF, município e CNES da unidade;
3. sexo;
4. UF e município de residência (habilita o campo de bairro);
5. código do bairro (o servidor devolve nome e categoria).

Só então faz o POST final com `form:botaoOk`. Cada evento usa o ViewState devolvido
pelo evento anterior.

## Problemas comuns

| Mensagem | Causa / solução |
|---|---|
| `Defina SINAN_USERNAME e SINAN_PASSWORD.` | Rode `configurar_credenciais.ps1` e reabra o terminal. |
| `O SINAN retornou para a tela de login.` | Usuário/senha incorretos ou senha expirada no SINAN. |
| `Falha de conexao. Nova tentativa em 60s.` | SINAN instável. O script tenta de novo sozinho (`--tentativas-login`, `--intervalo`). |
| `Evento AJAX nao encontrado: ...` | O SINAN mudou a tela. Não envie; investigue com `--simular`. |
| `Ficha com campos a preencher: ...` | Ainda há `PREENCHER` na ficha. |
| Bairro vem vazio na simulação | ID inexistente para o município ou município errado na ficha. |

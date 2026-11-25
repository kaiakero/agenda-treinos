# Agenda de Treinos

Sistema de agenda de treinos (no estilo TrainingPeaks/Treinus) feito para o trabalho de **bancos de dados orientados a documentos**.

Cada compromisso da agenda é um **treino** com data/horário, título, descrição e as **pessoas envolvidas** (treinador e atletas). Cada pessoa é guardada como um objeto separado dentro do documento do treino.

**Tecnologias:** Python + FastAPI (API), MongoDB (banco de documentos), HTML/CSS/JavaScript (página) e MongoDB Compass (ver os dados no banco).

---

## Sumário

1. [O que instalar](#1-o-que-instalar)
2. [Preparar o projeto](#2-preparar-o-projeto)
3. [Rodar o sistema](#3-rodar-o-sistema)
4. [Ver os dados no MongoDB Compass](#4-ver-os-dados-no-mongodb-compass)
5. [Como os dados ficam gravados](#5-como-os-dados-ficam-gravados)
6. [Funcionalidades e rotas da API](#6-funcionalidades-e-rotas-da-api)
7. [Estrutura do projeto](#7-estrutura-do-projeto)
8. [Problemas comuns](#8-problemas-comuns)

---

## 1. O que instalar

Você precisa de três programas: **Python**, **MongoDB Server** e **MongoDB Compass**.

### Windows (recomendado: winget)

Abra o **PowerShell** e rode um comando por vez:

```powershell
winget install --id Python.Python.3.13 -e --source winget
winget install --id MongoDB.Server -e --source winget
winget install --id MongoDB.Compass.Full -e --source winget
```

- Se o Windows pedir permissão de administrador, aceite.
- **Feche e abra o PowerShell de novo** depois de instalar, para ele reconhecer o `python`.
- O MongoDB Server é instalado como **serviço do Windows** e liga sozinho junto com o computador.

<details>
<summary>Sem winget? Instalação manual</summary>

| Programa | Link | Observação |
|---|---|---|
| Python 3.10 ou mais novo | <https://www.python.org/downloads/> | Marque **"Add python.exe to PATH"** na primeira tela do instalador |
| MongoDB Community Server | <https://www.mongodb.com/try/download/community> | Escolha o pacote `msi`, instalação **Complete**, deixe marcado **"Install MongoD as a Service"** |
| MongoDB Compass | <https://www.mongodb.com/try/download/compass> | O instalador do Server também oferece instalar o Compass |

</details>

<details>
<summary>macOS e Linux</summary>

**macOS** (com [Homebrew](https://brew.sh)):

```bash
brew install python
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
brew install --cask mongodb-compass
```

**Linux (Ubuntu/Debian):** instale o Python com `sudo apt install python3 python3-venv`, o MongoDB Server seguindo o [guia oficial](https://www.mongodb.com/docs/manual/administration/install-on-linux/) e o Compass pelo `.deb` em <https://www.mongodb.com/try/download/compass>. Depois ligue o banco com `sudo systemctl start mongod`.

Nesses sistemas, onde o README usa `.venv\Scripts\...`, troque por `.venv/bin/...` e use `python3` no lugar de `python`.

</details>

### Conferir se deu certo

```powershell
python --version
Get-Service MongoDB
```

O primeiro comando deve mostrar `Python 3.10` ou mais novo. O segundo deve mostrar o serviço `MongoDB` com status **Running**.

---

## 2. Preparar o projeto

### 2.1 Montar a pasta

Baixe os arquivos do Classroom e deixe-os nesta estrutura (os nomes das pastas importam):

```
agenda-treinos/
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── main.py
│   ├── schemas.py
│   └── static/
│       ├── app.js
│       ├── index.html
│       └── style.css
├── .env.example
├── README.md
├── requirements.txt
└── seed.py
```

> O arquivo `app/__init__.py` é vazio, mas precisa existir. Se ele não veio, crie um arquivo vazio com esse nome.

### 2.2 Abrir o terminal **dentro** da pasta

Todos os comandos a partir daqui rodam dentro de `agenda-treinos`:

```powershell
cd caminho\para\agenda-treinos
```

> Dica: no Explorador de Arquivos, abra a pasta `agenda-treinos`, clique na barra de endereço, digite `powershell` e aperte Enter.

### 2.3 Criar o ambiente virtual e instalar as dependências

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

Isso instala o FastAPI, o Uvicorn (servidor), o PyMongo (driver do MongoDB) e o python-dotenv dentro da pasta `.venv`, sem mexer no resto do computador.

### 2.4 Criar o arquivo de configuração `.env`

```powershell
copy .env.example .env
```

O conteúdo padrão já serve para o MongoDB instalado no próprio computador:

```
MONGO_URI=mongodb://localhost:27017
MONGO_DB=agenda_treinos
```

### 2.5 Popular o banco com treinos de exemplo

```powershell
.venv\Scripts\python seed.py
```

Deve aparecer: `4 treinos inseridos em 'agenda_treinos.treinos'.`

> O seed **apaga** todos os treinos existentes e cria 4 novos, com datas a partir de amanhã. Use antes da apresentação para ter dados limpos.

---

## 3. Rodar o sistema

```powershell
.venv\Scripts\python -m uvicorn app.main:app --reload
```

Deixe esse terminal aberto e acesse no navegador:

| Endereço | O que é |
|---|---|
| <http://127.0.0.1:8000> | A agenda (página principal) |
| <http://127.0.0.1:8000/docs> | Swagger: testa cada rota da API sem a página |
| <http://127.0.0.1:8000/health> | Mostra se a API e o MongoDB estão respondendo |

Para parar o servidor, aperte **Ctrl + C** no terminal.

> Não abra o `index.html` com duplo clique. A página precisa ser aberta pelo endereço acima, senão ela não consegue falar com a API.

---

## 4. Ver os dados no MongoDB Compass

### 4.1 Conectar

1. Abra o **MongoDB Compass**.
2. Clique em **Add new connection** (ou **+** ao lado de *Connections*).
3. Em **URI**, deixe `mongodb://localhost:27017`.
4. Clique em **Save & Connect**.

### 4.2 Abrir a coleção

Na barra lateral, clique em **`agenda_treinos`** e depois em **`treinos`**. Cada item da lista é um documento (um treino).

> O banco `agenda_treinos` só aparece depois que você rodar o `seed.py` ou cadastrar o primeiro treino pela página.

### 4.3 Modos de visualização

No canto superior direito da lista de documentos há três botões:

- **List**: cada documento como uma árvore. Clique na setinha de `participantes` para abrir a lista de pessoas.
- **{} JSON**: o documento como texto. É o melhor modo para mostrar a estrutura na apresentação.
- **Table**: visão em tabela. Note que `participantes` aparece como `Array`, porque as pessoas estão dentro do documento.

### 4.4 Buscas úteis

Digite no campo **Filter** e clique em **Find**:

| Filtro | O que mostra |
|---|---|
| `{ "participantes.nome": "Vitor" }` | Treinos em que o Vitor participa |
| `{ "participantes.papel": "treinador" }` | Treinos com treinador |
| `{ "modalidade": "corrida" }` | Só os treinos de corrida |
| `{ "duracao_prevista_min": { "$exists": false } }` | Treinos sem duração (mostra que o esquema é flexível) |
| `{ "data_hora": { "$gte": ISODate("2026-11-26") } }` | Treinos a partir de 26/11 |

Para ordenar por data, clique em **Options** e coloque `{ "data_hora": 1 }` em **Sort**.

### 4.5 Ver as mudanças acontecendo

Deixe o Compass e a página lado a lado. Faça uma ação na página (cadastrar, editar, remover pessoa, excluir) e clique em **Refresh** no Compass: o documento aparece alterado.

---

## 5. Como os dados ficam gravados

Banco `agenda_treinos`, coleção `treinos`. Exemplo de documento:

```json
{
  "_id": { "$oid": "6b061ab2fb3d2af92580576b" },
  "data_hora": { "$date": "2026-11-25T07:00:00Z" },
  "titulo": "Intervalado 6x800m",
  "descricao": "Aquecimento 15min Z1-Z2; 6x800m @3:50/km com 2min trote; desaquecimento 10min",
  "modalidade": "corrida",
  "duracao_prevista_min": 60,
  "status": "planejado",
  "participantes": [
    { "nome": "Ana Souza",  "papel": "treinador", "id": "6e6c9819" },
    { "nome": "Vitor",      "papel": "atleta",    "id": "701f11cc" },
    { "nome": "Bruno Lima", "papel": "atleta",    "id": "24d83cbc" }
  ]
}
```

| Campo | Tipo | Observação |
|---|---|---|
| `_id` | ObjectId | Gerado pelo MongoDB |
| `data_hora` | Date | Data e horário do treino |
| `titulo` | String | Obrigatório |
| `descricao` | String | Estrutura do treino |
| `modalidade` | String | `corrida`, `ciclismo`, `natacao`, `forca` ou `outro` |
| `duracao_prevista_min` | Int | **Opcional**: alguns documentos têm, outros não |
| `status` | String | `planejado` ao cadastrar |
| `participantes` | Array de objetos | Cada pessoa com `id`, `nome` e `papel` (`treinador` ou `atleta`) |

**Por que as pessoas ficam dentro do treino?** Num banco relacional seriam três tabelas (treinos, pessoas e uma tabela de ligação) e um JOIN para montar a agenda. No MongoDB o treino inteiro vem numa leitura só. Cada pessoa continua individual: tem seu próprio `id` e pode ser alterada ou removida sozinha com `$set` e `$pull`.

> O `Z` no fim da data significa UTC, mas o valor gravado é o horário local. A página mostra o horário certo.

---

## 6. Funcionalidades e rotas da API

| Funcionalidade (enunciado) | Na página | Rota | Operação no MongoDB |
|---|---|---|---|
| Listar compromissos | Tela inicial | `GET /treinos` | `find().sort("data_hora")` |
| Cadastrar novo compromisso | **+ Novo treino** | `POST /treinos` | `insert_one` |
| Alterar título e descrição | **Editar título/descrição** | `PATCH /treinos/{id}` | `$set` só nos campos enviados |
| Alterar as pessoas envolvidas | **Alterar participantes** | `PUT /treinos/{id}/participantes` | `$set` no array |
| Excluir uma pessoa | **×** ao lado do nome | `DELETE /treinos/{id}/participantes/{pid}` | `$pull` |
| Excluir um compromisso | **Excluir treino** | `DELETE /treinos/{id}` | `delete_one` |

Rotas extras (só pela API/Swagger):

| Rota | Operação |
|---|---|
| `POST /treinos/{id}/participantes` | Adiciona uma pessoa (`$push`) |
| `PATCH /treinos/{id}/participantes/{pid}` | Altera uma pessoa (`$set` com operador posicional `$`) |

---

## 7. Estrutura do projeto

| Arquivo | Função |
|---|---|
| `app/db.py` | Conexão com o MongoDB (lê o `.env`) e criação dos índices |
| `app/schemas.py` | Modelos que validam os dados (Treino, Participante) |
| `app/main.py` | Rotas da API e as operações no MongoDB |
| `app/static/index.html` | Estrutura da página e dos formulários |
| `app/static/app.js` | Chama a API e monta a agenda na tela |
| `app/static/style.css` | Visual da página |
| `seed.py` | Apaga e recria os treinos de exemplo |
| `requirements.txt` | Lista de dependências Python |
| `.env.example` | Modelo do arquivo de configuração |

---

## 8. Problemas comuns

| Erro | Causa | Solução |
|---|---|---|
| `Não foi possível carregar o módulo '.venv'` | Terminal fora da pasta do projeto | `cd` para dentro de `agenda-treinos` (passo 2.2) |
| `python` não é reconhecido | Python fora do PATH | Feche e abra o terminal; se continuar, reinstale marcando "Add python.exe to PATH" |
| `No module named fastapi` (ou `uvicorn`, `pymongo`) | Dependências não instaladas, ou usando o Python errado | Rode o passo 2.3 e sempre use `.venv\Scripts\python` |
| `MongoDB não respondeu` / `MongoDB indisponível` | Serviço do MongoDB parado | No PowerShell **como administrador**: `Start-Service MongoDB` |
| `Get-Service MongoDB` não encontra nada | MongoDB Server não instalado como serviço | Reinstale marcando "Install MongoD as a Service" |
| `[Errno 10048]` ou porta 8000 em uso | Outro servidor já está rodando | Feche o outro terminal ou use `--port 8001` |
| Página parada em "Carregando…" ou "Abra pelo servidor" | `index.html` aberto direto do arquivo | Acesse <http://127.0.0.1:8000> com o servidor rodando |
| Compass não mostra o banco `agenda_treinos` | Banco ainda vazio | Rode `.venv\Scripts\python seed.py` e clique em **Refresh** no Compass |

---

## Entrega no Classroom

Envie os arquivos soltos (sem compactar) da estrutura do passo 2.1. **Não envie** a pasta `.venv` (é gerada pelo `pip install`), o arquivo `.env` nem pastas `__pycache__`.

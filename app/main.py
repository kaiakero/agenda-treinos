"""API da Agenda de Treinos.

Rodar:  uvicorn app.main:app --reload
Swagger: http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager
from pathlib import Path

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pymongo import ReturnDocument

from . import db
from .schemas import (
    Participante,
    ParticipanteIn,
    Status,
    Treino,
    TreinoIn,
    TreinoUpdateTexto,
    treino_from_doc,
)

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    if db.ping():
        db.criar_indices()
    else:
        print("AVISO: MongoDB não respondeu. Confira MONGO_URI no arquivo .env")
    yield


app = FastAPI(title="Agenda de Treinos", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", tags=["infra"])
def health():
    return {"api": "ok", "mongo": "ok" if db.ping() else "indisponivel"}


# ---------------- auxiliares ----------------

def _oid(treino_id: str) -> ObjectId:
    """Converte o id da URL em ObjectId (404 se o formato for inválido)."""
    try:
        return ObjectId(treino_id)
    except (InvalidId, TypeError):
        raise HTTPException(404, "Treino não encontrado")


def _atualizar(treino_id: str, filtro_extra: dict, operacao: dict) -> Treino:
    """Aplica um update e devolve o treino já alterado (404 se não achou)."""
    doc = db.treinos.find_one_and_update(
        {"_id": _oid(treino_id), **filtro_extra},
        operacao,
        return_document=ReturnDocument.AFTER,
    )
    if doc is None:
        raise HTTPException(404, "Treino não encontrado")
    return treino_from_doc(doc)


def _participantes_docs(lista: list[ParticipanteIn]) -> list[dict]:
    """Cada pessoa vira um objeto próprio, com id individual."""
    return [Participante(**p.model_dump()).model_dump() for p in lista]


# ---------------- treinos ----------------

@app.get("/treinos", response_model=list[Treino], tags=["treinos"])
def listar_treinos():
    """Lista compromissos ordenados por data/horário."""
    if not db.ping():
        raise HTTPException(503, "MongoDB indisponível. Confira MONGO_URI no arquivo .env")
    return [treino_from_doc(d) for d in db.treinos.find().sort("data_hora", 1)]


@app.post("/treinos", response_model=Treino, status_code=201, tags=["treinos"])
def cadastrar_treino(treino: TreinoIn):
    """Cadastra um novo compromisso (insert_one)."""
    doc = treino.model_dump(exclude={"participantes"}, exclude_none=True)
    doc["status"] = Status.planejado.value
    doc["participantes"] = _participantes_docs(treino.participantes)
    resultado = db.treinos.insert_one(doc)
    return treino_from_doc({**doc, "_id": resultado.inserted_id})


@app.patch("/treinos/{treino_id}", response_model=Treino, tags=["treinos"])
def alterar_titulo_descricao(treino_id: str, dados: TreinoUpdateTexto):
    """Altera título e/ou descrição ($set só nos campos enviados)."""
    campos = dados.model_dump(exclude_none=True)
    if not campos:
        raise HTTPException(400, "Envie 'titulo' e/ou 'descricao'")
    return _atualizar(treino_id, {}, {"$set": campos})


@app.delete("/treinos/{treino_id}", status_code=204, tags=["treinos"])
def excluir_treino(treino_id: str):
    """Exclui o compromisso inteiro (delete_one)."""
    if db.treinos.delete_one({"_id": _oid(treino_id)}).deleted_count == 0:
        raise HTTPException(404, "Treino não encontrado")
    return Response(status_code=204)


# ---------------- participantes ----------------

@app.put("/treinos/{treino_id}/participantes", response_model=Treino, tags=["participantes"])
def substituir_participantes(treino_id: str, participantes: list[ParticipanteIn]):
    """Troca a lista inteira de pessoas ($set no array)."""
    return _atualizar(treino_id, {}, {"$set": {"participantes": _participantes_docs(participantes)}})


@app.post("/treinos/{treino_id}/participantes", response_model=Treino, tags=["participantes"])
def adicionar_participante(treino_id: str, participante: ParticipanteIn):
    """Adiciona uma pessoa ao treino ($push)."""
    novo = _participantes_docs([participante])[0]
    return _atualizar(treino_id, {}, {"$push": {"participantes": novo}})


@app.patch("/treinos/{treino_id}/participantes/{participante_id}", response_model=Treino, tags=["participantes"])
def alterar_participante(treino_id: str, participante_id: str, participante: ParticipanteIn):
    """Altera nome/papel de UMA pessoa (operador posicional $)."""
    return _atualizar(
        treino_id,
        {"participantes.id": participante_id},
        {"$set": {
            "participantes.$.nome": participante.nome,
            "participantes.$.papel": participante.papel,
        }},
    )


@app.delete("/treinos/{treino_id}/participantes/{participante_id}", response_model=Treino, tags=["participantes"])
def remover_participante(treino_id: str, participante_id: str):
    """Remove uma pessoa do treino ($pull)."""
    return _atualizar(
        treino_id,
        {"participantes.id": participante_id},
        {"$pull": {"participantes": {"id": participante_id}}},
    )

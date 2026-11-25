"""Modelos (Pydantic) que validam o que entra e sai da API.

Cada treino guarda os participantes como uma LISTA DE OBJETOS embutida
no próprio documento — cada pessoa é armazenada individualmente.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class Papel(str, Enum):
    treinador = "treinador"
    atleta = "atleta"


class Modalidade(str, Enum):
    corrida = "corrida"
    ciclismo = "ciclismo"
    natacao = "natacao"
    forca = "forca"
    outro = "outro"


class Status(str, Enum):
    planejado = "planejado"
    concluido = "concluido"


# ---------- Participantes ----------

class ParticipanteIn(BaseModel):
    model_config = ConfigDict(use_enum_values=True)  # grava "atleta", não Papel.atleta
    nome: str = Field(min_length=1, examples=["Ana Souza"])
    papel: Papel = Papel.atleta


class Participante(ParticipanteIn):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])


# ---------- Treinos ----------

class TreinoIn(BaseModel):
    """Corpo para cadastrar um treino."""
    model_config = ConfigDict(use_enum_values=True)
    data_hora: datetime = Field(examples=["2026-11-26T07:00:00"])
    titulo: str = Field(min_length=1, examples=["Intervalado 6x800m"])
    descricao: str = Field(default="", examples=["Aquecimento 15min; 6x800m @3:50/km; desaquecimento 10min"])
    modalidade: Modalidade = Modalidade.corrida
    duracao_prevista_min: Optional[int] = Field(default=None, ge=1)
    participantes: list[ParticipanteIn] = []


class TreinoUpdateTexto(BaseModel):
    """Corpo para alterar título e/ou descrição."""
    titulo: Optional[str] = Field(default=None, min_length=1)
    descricao: Optional[str] = None


class Treino(BaseModel):
    """Treino como é devolvido pela API."""
    id: str
    data_hora: datetime
    titulo: str
    descricao: str = ""
    modalidade: Modalidade = Modalidade.corrida
    duracao_prevista_min: Optional[int] = None
    status: Status = Status.planejado
    participantes: list[Participante] = []


def treino_from_doc(doc: dict) -> Treino:
    """Converte um documento do MongoDB (com _id ObjectId) para o modelo da API."""
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    return Treino(**doc)

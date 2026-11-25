"""Conexão com o MongoDB.

Lê MONGO_URI e MONGO_DB do arquivo .env (ou das variáveis de ambiente).
"""
import os

from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "agenda_treinos")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[MONGO_DB]

# Coleção principal: cada documento é um treino (compromisso da agenda)
treinos = db["treinos"]


def criar_indices() -> None:
    """Índices usados pela listagem e pelas operações em participantes."""
    treinos.create_index([("data_hora", ASCENDING)])
    treinos.create_index("participantes.id")


def ping() -> bool:
    """Retorna True se o servidor MongoDB responder."""
    try:
        client.admin.command("ping")
        return True
    except Exception:
        return False

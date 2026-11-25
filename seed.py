"""Popula o banco com treinos de exemplo (apaga os existentes).

Uso:  python seed.py
"""
from datetime import datetime, timedelta

from app import db
from app.schemas import Participante


def p(nome: str, papel: str = "atleta") -> dict:
    return Participante(nome=nome, papel=papel).model_dump()


def main() -> None:
    if not db.ping():
        raise SystemExit("MongoDB não respondeu. Confira MONGO_URI no .env")

    base = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
    treinador = p("Ana Souza", "treinador")

    treinos = [
        {
            "data_hora": base + timedelta(days=1),
            "titulo": "Intervalado 6x800m",
            "descricao": "Aquecimento 15min Z1-Z2; 6x800m @3:50/km com 2min trote; desaquecimento 10min",
            "modalidade": "corrida",
            "duracao_prevista_min": 60,
            "status": "planejado",
            "participantes": [treinador, p("Vitor"), p("Bruno Lima")],
        },
        {
            "data_hora": base + timedelta(days=2, hours=11),
            "titulo": "Fortalecimento — membros inferiores",
            "descricao": "3x12 agachamento, 3x10 afundo, 3x15 elevação de panturrilha, prancha 3x40s",
            "modalidade": "forca",
            "duracao_prevista_min": 45,
            "status": "planejado",
            "participantes": [treinador, p("Vitor")],
        },
        {
            "data_hora": base + timedelta(days=3),
            "titulo": "Regenerativo 6 km",
            "descricao": "Rodagem leve em Z1, cadência solta",
            "modalidade": "corrida",
            "status": "planejado",  # sem duracao_prevista_min: esquema flexível
            "participantes": [p("Vitor"), p("Carla Mendes")],
        },
        {
            "data_hora": base + timedelta(days=5, hours=-1),
            "titulo": "Longão 14 km",
            "descricao": "Ritmo confortável (5:40-5:50/km); últimos 2 km no ritmo de prova",
            "modalidade": "corrida",
            "duracao_prevista_min": 80,
            "status": "planejado",
            "participantes": [treinador, p("Vitor"), p("Bruno Lima"), p("Carla Mendes")],
        },
    ]

    db.treinos.delete_many({})
    resultado = db.treinos.insert_many(treinos)
    db.criar_indices()
    print(f"{len(resultado.inserted_ids)} treinos inseridos em '{db.MONGO_DB}.treinos'.")


if __name__ == "__main__":
    main()

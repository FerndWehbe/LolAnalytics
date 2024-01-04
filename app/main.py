import json

from celery.result import AsyncResult
from database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models import Match, Player, PlayerMatchAssociation
from mongo import find_match_by_id
from repository import get_player, get_player_by_name
from tasks import get_summoner_info
from utils import create_rewind

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(
    bind=engine,
    tables=[
        Player.__table__,
        Match.__table__,
        PlayerMatchAssociation.__table__,
    ],
    checkfirst=True,
)


@app.get("/check")
async def check(name: str, region: str) -> dict:
    """
    Rota Verifica se um jogador existe no banco de dados.
    Se não existir, inicia uma tarefa assíncrona para buscar informações do \
    jogador.

    Args:
        name (str): Nome do jogador no formato 'nick_name#riot_id'.
        region (str): Região do jogador.

    Returns:
        dict: Retorna um dicionário indicando a existência do jogador,
        o próprio jogador se existir, ou o ID da tarefa.
    """
    nick_name, riot_id = name.split("#")
    player: Player = get_player_by_name(player_name=nick_name)

    if player and player.rewind_id is not None:
        return {"exists": True, "player": player}

    task = get_summoner_info.delay(nick_name, riot_id, region)

    return {"exists": False, "task_id": task.id}


@app.get("/get_task_result/{task_id}")
async def get_task_result(task_id: str) -> dict:
    """
    Rota que obtém o resultado de uma tarefa assíncrona pelo seu ID.

    Args:
        task_id (str): ID da tarefa.

    Returns:
        dict: Retorna o estado da tarefa e seu resultado, se estiver concluída.
    """
    task = AsyncResult(task_id)

    task_state = task.state
    result = None

    if task_state == "SUCCESS":
        result = task.result
        player = get_player(result["dados"]["puuid"])
        player = player.to_dict()

        return {
            "task_state": task_state,
            "next_task": result["next_task"],
            "player": player,
            "task_id": result["task_id"],
        }

    return {"task_state": task_state, "message": "Processando dados."}


@app.delete("/delete_task_from_id/{task_id}")
async def delete_task_from_id(task_id: str) -> dict:
    """
    Rota que deleta uma tarefa assíncrona pelo seu ID.

    Args:
        task_id (str): ID da tarefa.

    Returns:
        dict: Mensagem indicando se a tarefa foi deletada ou não encontrada.
    """
    result = AsyncResult(task_id)
    if result:
        result.revoke()
        return {"message": f"Task {task_id} deletada com sucesso"}
    return {"message": f"Task {task_id} não encontrada"}


@app.get("/summoner_statistics")
async def summoner_statistics(summoner_name: str) -> dict:
    """
    Rota que retorna estatísticas do invocador.

    Args:
        summoner_name (str): Nome do invocador.

    Returns:
        dict: Retorna um dicionários mostrando as estatisticas do jogador durante o ano.
    """
    with open("./utils/statistics_example.json") as f:
        statistics = json.load(f)
    if statistics:
        return JSONResponse(content=statistics)
    return {"message": "Estatistica ainda não gerada!"}


@app.get("/summoner_statistics_by_puuid/{puuid}")
async def summoner_statistics_by_puuid(puuid: str) -> dict:
    return JSONResponse(
        content=create_rewind(puuid),
    )


@app.get("/get_match_info_by_match_id/{match_id}")
async def get_match_info_by_match_id(match_id: str) -> dict:
    document = find_match_by_id(match_id)
    if document:
        json_result = json.dumps(document, default=str)
        return JSONResponse(content=json_result, media_type="application/json")
    return JSONResponse(content={"error": "Documento não encontrado"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)

from celery.result import AsyncResult
from database import Base, engine
from fastapi import FastAPI
from models import Match, Player, PlayerMatchAssociation
from repository import get_player_by_name
from tasks import get_summoner_info

app = FastAPI()

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
async def check(name: str, region: str):
    nick_name, riot_id = name.split("#")
    player: Player = get_player_by_name(player_name=nick_name)

    if player and player.rewind_id is not None:
        return {"exists": True, "player": player}

    task = get_summoner_info.delay(nick_name, riot_id, region)

    return {"exists": False, "task_id": task.id}


@app.get("/get_task_result")
async def get_task_result(task_id: str):
    task = AsyncResult(task_id)
    task.name
    return {"task_state": task.state}


@app.delete("/delete_task_from_id/{task_id}")
async def delete_task_from_id(task_id: str):
    result = AsyncResult(task_id).revoke()
    if result:
        return {"message": f"Task {task_id} deletada com sucesso"}
    return {"message": f"Task {task_id} não encontrada"}


@app.get("/summoner_statistics")
async def summoner_statistics(summoner_name: str):
    return {"message": "Estatistica ainda não gerada!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)

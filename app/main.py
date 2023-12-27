from celery.result import AsyncResult
from database import Base, SessionLocal, engine
from fastapi import FastAPI
from models import Player
from tasks import get_summoner_info

app = FastAPI()

Base.metadata.create_all(bind=engine, tables=[Player.__table__], checkfirst=True)


def get_player(name: str) -> Player:
    db = SessionLocal()
    user = db.query(Player).filter(Player.name == name).first()
    db.close()
    return user


@app.get("/check")
async def check(name: str, region: str):
    nick_name, riot_id = name.split("#")
    player = get_player(nick_name)

    if player:
        return {"exists": True, "player": player}
    task = get_summoner_info(nick_name, riot_id, region)
    return {"exists": False, "task_id": task.id}


@app.get("/get_task_result")
async def get_task_result(task_id: str):
    task = AsyncResult(task_id)
    return {"task_state": task.state}


@app.get("/summoner_statistics")
async def summoner_statistics(summoner_name: str):
    return {"message": "Estatistica ainda não gerada!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)

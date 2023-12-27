from fastapi import FastAPI
from tasks import exemplo_task

app = FastAPI()


@app.get("/summoner_statistics")
async def summoner_statistics(summoner_name: str):
    print(summoner_name)
    exemplo_task.delay("teste")
    return {"message": "Estatistica ainda não gerada!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)

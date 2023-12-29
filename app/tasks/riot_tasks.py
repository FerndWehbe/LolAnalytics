import os
from pickle import dumps

from celery import shared_task
from database import engine
from dotenv import load_dotenv
from models import Match, Player
from repository import create_player
from riot_api.lol_api import LolApi
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from utils import get_timestamp_from_year

from .celery_app import celery_app


@celery_app.task()
def base_task():
    return None


def get_matchs_ids(
    lol_api: LolApi,
    puuid: str,
    region: str,
    start_time: int,
    start: int,
    count: int,
    list_ids: list = None,
) -> list:
    if list_ids is None:
        list_ids = []

    ids = lol_api.get_matchs_ids(puuid, region, start, count, start_time)

    if ids is None:
        return list_ids

    list_ids = list_ids + ids

    if len(ids) < 100:
        return list_ids

    return get_matchs_ids(
        lol_api,
        puuid,
        region,
        start_time,
        start=count + start + 1,
        count=count,
        list_ids=list_ids,
    )


@shared_task
def get_summoner_info(nick_name: str, riot_id: str, region: str) -> bytes:
    load_dotenv()

    lol_api = LolApi(os.environ.get("riot_api_key"))
    dados = lol_api.get_summoner_info_riot_id(nick_name, riot_id, region)

    player = Player(puuid=dados.puuid, name=dados.name, riot_id=riot_id)

    player = create_player(player=player)

    task_matchs = get_all_matchs_id.delay(dados.puuid, region)

    return dumps({"dados": dados, "task_id": task_matchs.id})


@shared_task
def get_all_matchs_id(puuid: str, region: str, year: int = 2023) -> list:
    load_dotenv()

    lol_api = LolApi(os.environ.get("riot_api_key"))
    list_all_ids = get_matchs_ids(
        lol_api,
        puuid,
        lol_api._regions[region],
        start_time=get_timestamp_from_year(year),
        start=0,
        count=100,
    )

    list_match = [Match(match_id=match_id) for match_id in list_all_ids]

    session = Session(engine)

    try:
        session.add_all(list_match)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        print(f"Erro de integridade: {e}")
        for obj in list_match:
            try:
                session.add(obj)
                session.commit()
            except IntegrityError:
                session.rollback()
                print(
                    f"Objeto não adicionado devido a violação de chave primaria: {obj}"
                )
    finally:
        session.close()

    return list_all_ids


@shared_task
def get_infos_from_list_matchs(list_matchs_ids: list, region: str):
    load_dotenv()

    lol_api = LolApi(os.environ.get("riot_api_key"))

    for match in list_matchs_ids:
        lol_api.get_match_infos_by_id(match, region)

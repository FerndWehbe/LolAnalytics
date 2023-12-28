import os
from pickle import dumps

from celery import shared_task
from database import engine
from dotenv import load_dotenv
from models import Match
from riot_api.lol_api import LolApi
from sqlalchemy.orm import SessionMaker
from utils import get_timestamp_from_year


def get_matchs_ids(lol_api, puuid, region, start_time, start, count, list_ids=None): # noqa
    if not list_ids:
        list_ids = []
    ids = lol_api.get_matchs_ids(puuid, region, start_time, start, count)
    list_ids += ids
    if len(ids) < 100:
        return list_ids
    get_matchs_ids(
        lol_api,
        puuid,
        region,
        start_time,
        start=count+1,
        count=count,
        list_ids=list_ids
    )
    

@shared_task
def get_summoner_info(nick_name: str, riot_id: str, region: str) -> bytes:
    load_dotenv()

    lol_api = LolApi(os.environ.get("riot_api_key"))
    dados = lol_api.get_summoner_info_riot_id(nick_name, riot_id, region)

    return dumps(dados)


@shared_task
def get_all_matchs_id(puuid: str, region: str, year: int = 2023):
    load_dotenv()

    lol_api = LolApi(os.environ.get("riot_api_key"))
    ids = get_matchs_ids(lol_api, puuid, lol_api._regions[region], start_time=get_timestamp_from_year(year), start=0, count=100) # noqa
    list_match = [Match(match_id=match_id) for match_id in ids]

    session = SessionMaker(engine)
    session.add_all(list_match)

    session.commit()

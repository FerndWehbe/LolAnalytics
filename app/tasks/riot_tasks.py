import os
from pickle import dumps

from celery import shared_task
from dotenv import load_dotenv
from riot_api.lol_api import LolApi


@shared_task
def get_summoner_info(nick_name, riot_id, region):
    load_dotenv()

    lol_api = LolApi(os.environ.get("riot_api_key"))
    dados = lol_api.get_summoner_info_riot_id(nick_name, riot_id, region)

    return dumps(dados)

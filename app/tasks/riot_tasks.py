import os
from pickle import dumps

from celery import shared_task
from dotenv import load_dotenv
from models import Match, Player, PlayerMatchAssociation
from mongo import insert_match_data
from repository import (
    create_match,
    create_player,
    create_player_match_association,
    get_match,
    get_matches_not_searched_by_puuid,
    get_player,
    update_match,
)
from riot_api.lol_api import LolApi
from sqlalchemy.exc import IntegrityError
from utils import RateLimiter, get_timestamp_from_year

from .celery_app import celery_app

MATCH_INFO_TASK_PRIORITY = 3
MATCH_LIST_TASK_PRIORITY = 4
PLAYER_INFO_TASK_PRIORITY = 5
PLAYER_INFO_FAIL_TASK_PRIORITY = 10

rate_limiter = RateLimiter(20, 80, 1, 120)


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
    """
    Obtém os IDs das partidas de um jogador com base nos parâmetros fornecidos.

    Args:
        lol_api (LolApi): Instância da API do League of Legends.
        puuid (str): Identificador único do jogador.
        region (str): Região do jogador.
        start_time (int): Carimbo de tempo inicial para a busca de partidas.
        start (int): Índice inicial.
        count (int): Número de partidas a serem buscadas.
        list_ids (list, opcional): Lista de IDs para adicionar.

    Returns:
        list: Lista contendo os IDs das partidas.
    """
    if list_ids is None:
        list_ids = []

    rate_limiter.make_request()
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
    """
    Obtém informações sobre um invocador do League of Legends e suas partidas.

    Args:
        nick_name (str): Apelido in-game do invocador.
        riot_id (str): ID do invocador no Riot.
        region (str): Região do invocador.

    Returns:
        bytes: Dados serializados contendo detalhes do invocador e o ID da \
        tarefa para busca de informações das partidas.
    """
    load_dotenv()

    lol_api = LolApi(os.environ.get("riot_api_key"))

    rate_limiter.make_request()
    dados = lol_api.get_summoner_info_riot_id(nick_name, riot_id, region)

    player = Player(puuid=dados.puuid, name=dados.name, riot_id=riot_id)
    try:
        player = create_player(player=player)
    except IntegrityError as e:
        print(f"Player já registrado porem não possui rewind gerada. {e}")

    task_matchs = get_all_matchs_id.delay(dados.puuid, region)

    return dumps({"dados": dados, "task_id": task_matchs.id})


@shared_task
def get_all_matchs_id(puuid: str, region: str, year: int = 2023) -> list:
    """
    Obtém todos os IDs de partidas de um jogador dentro de um ano específico.

    Args:
        puuid (str): Identificador único do jogador.
        region (str): Região do jogador.
        year (int, opcional): Ano para busca das partidas. Padrão é 2023.

    Returns:
        list: Dados serializados contendo os IDs das partidas e o ID da tarefa \
        para busca de informações das partidas.
    """
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

    player = get_player(player_puuid=puuid)

    list_match = [Match(match_id=match_id) for match_id in list_all_ids]

    for obj in list_match:
        try:
            create_match(match=obj)
        except IntegrityError:
            pass

    for match in list_match:
        try:
            create_player_match_association(
                player_match=PlayerMatchAssociation(
                    player_puuid=player.puuid, match_id=match.match_id
                )
            )
        except IntegrityError:
            pass

    match_task = get_infos_from_list_matchs.delay(puuid, region)

    return dumps({"dados": list_all_ids, "task_id": match_task.id})


@shared_task
def get_infos_from_list_matchs(puuid: str, region: str) -> list:
    """
    Obtém informações de uma lista de partidas não pesquisadas de um jogador.

    Args:
        puuid (str): Identificador único do jogador.
        region (str): Região do jogador.

    Returns:
        None: Retorna com base no progresso da busca por informações das \
        partidas.
    """
    load_dotenv()

    lol_api = LolApi(os.environ.get("riot_api_key"))

    list_matchs_ids = get_matches_not_searched_by_puuid(player_puuid=puuid)

    print(f"Faltam: {len(list_matchs_ids)} a serem buscadas")

    list_matchs_failure = []

    for match_id in list_matchs_ids:
        try:
            rate_limiter.make_request()
            match_info = lol_api.get_match_infos_by_id(match_id, region)
            insert_match_data(match_info)
            match = get_match(match_id=match_id)
            match.is_searched = True
            match = update_match(match_id=match_id, updated_match=match)
        except Exception:
            list_matchs_failure.append(match_id)

    if list_matchs_failure:
        task_matchs_failure = get_infos_from_list_matchs_failed.delay(
            puuid, region, list_matchs_failure
        )
        return {
            "mensagem": (
                f"Foram recuperadas "
                f"{len(list_matchs_ids) - len(list_matchs_failure)}"
                f" de {len(list_matchs_ids)}. Iniciando tentativa de buscar as"
                f" {len(list_matchs_failure)} tasks faltantes."
            ),
            "task_id": task_matchs_failure.id,
        }


@shared_task
def get_infos_from_list_matchs_failed(
    puuid: str, region: str, list_matchs_fail: list[str]
):
    """
    Obtém informações de partidas que falharam em buscas anteriores.

    Args:
        puuid (str): Identificador único do jogador.
        region (str): Região do jogador.
        list_matchs_fail (list[str]): Lista de IDs de partidas que falharam em \
        buscas anteriores.

    Returns:
        dict: Informações sobre as partidas que ainda não foram encontradas.
    """
    load_dotenv()

    lol_api = LolApi(os.environ.get("riot_api_key"))

    print(f"Faltam: {list_matchs_fail} a serem buscadas")

    falhas = []

    for match_id in list_matchs_fail:
        try:
            rate_limiter.make_request()
            match_info = lol_api.get_match_infos_by_id(match_id, region)
            insert_match_data(match_info)
            match = get_match(match_id=match_id)
            match.is_searched = True
            match = update_match(match_id=match_id, updated_match=match)
        except Exception:
            falhas.append(match_id)
    return {
        "mensagem": f"{len(falhas)} partida não foram encontradas no momento.",
        "dados": falhas,
    }

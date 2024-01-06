from exceptions import PlayerNotFound

from .base_api import BaseRiotApi
from .summoner_dto import Summoner


# TODO melhorar o tratamento de exceção
class LolApi(BaseRiotApi):
    def __init__(self, token: str) -> None:
        super().__init__()
        self.token = token
        self._headers["X-Riot-Token"] = self.token

    def get_summoner_info_riot_id(
        self, game_name: str, tag_line: str, server_account: str = "br1"
    ) -> Summoner:
        puuid = self._get_puuid_by_riot_id(
            game_name, tag_line, self._regions[server_account]
        )
        final_url = f"/lol/summoner/v4/summoners/by-puuid/{puuid}"

        response = self._get(self._get_base_url_region(server_account) + final_url)

        if response.status_code == 200:
            return Summoner(**response.json())

        if response.status_code == 404:
            raise PlayerNotFound(
                f"Player de nick {game_name} não encontrado "
                "ou riot_id {tag_line} está invalido."
            )

        raise Exception(
            f"Falha na requisição para puuid: {puuid}. "
            "Status Code: {response.status_code}"
        )

    def get_summoner_info_by_puuid(self, puuid: str, server_account: str = "br1"):
        final_url = f"/lol/summoner/v4/summoners/by-puuid/{puuid}"
        response = self._get(self._get_base_url_region(server_account) + final_url)

        if response.status_code == 200:
            return Summoner(**response.json())

        raise Exception(
            f"Falha na requisição para puuid: {puuid}. "
            "Status Code: {response.status_code}"
        )

    def _get_puuid_by_riot_id(
        self, game_name: str, tag_line: str, server_account: str = "americas"
    ):
        final_url = f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"

        response = self._get(self._get_base_url_region(server_account) + final_url)

        if response.status_code == 200:
            return response.json()["puuid"]
        raise Exception(f"Falha na requisição. Status Code: {response.status_code}")

    def get_matchs_ids(
        self,
        summoner_puuid: str,
        match_region: str = "americas",
        start: int = 0,
        count: int = 20,
        startTime: int = None,
        endTime: int = None,
        queue: int = None,
        type: str = None,
    ):
        final_url = (
            f"/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids?{start=}&{count=}"
        )

        if startTime:
            final_url += f"&{startTime=}"

        if endTime:
            final_url += f"&{endTime=}"

        if queue:
            final_url += f"&{queue=}"

        if type:
            final_url += f"&{type=}"

        response = self._get(self._get_base_url_region(match_region) + final_url)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Falha na requisição. Status Code: {response.status_code}")

    def get_match_infos_by_id(self, match_id: str, region: str):
        final_url = f"/lol/match/v5/matches/{match_id}"

        response = self._get(
            self._get_base_url_region(self._regions[region]) + final_url
        )

        if response.status_code == 200:
            return response.json()

        print(self._get_base_url_region(region) + final_url)
        raise Exception(f"Falha ma requisição. Status Code: {response.status_code}")

    def get_league_entries_infos_by_summoner(self, summoner_id: str, region: str):
        final_url = f"/lol/league/v4/entries/by-summoner/{summoner_id}"

        response = self._get(self._get_base_url_region(region) + final_url)

        if response.status_code == 200:
            return response.json()

        raise Exception(f"Falha ma requisição. Status Code: {response.status_code}")

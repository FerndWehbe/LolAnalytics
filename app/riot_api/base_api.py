from httpx import Client, Response


class BaseRiotApi:
    def __init__(self) -> None:
        self._client = Client()
        self._headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
        }
        self._reagions = {
            "br1": "americas",
            "eun1": "europe",
            "kr": "asia",
            "oc1": "sea",
        }

    def _get(self, url: str) -> Response:
        return self._client.get(url=url, headers=self._headers)

    def _get_base_url_region(self, region: str = "br1") -> str:
        return f"https://{region}.api.riotgames.com"

    def __del__(self) -> None:
        self._client.close()

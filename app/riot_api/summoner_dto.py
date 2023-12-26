class Summoner:
    def __init__(
        self,
        id: str,
        accountId: str,
        puuid: str,
        name: str,
        profileIconId: int,
        revisionDate: int,
        summonerLevel: int,
    ) -> None:
        self.id = id
        self.account_id = accountId
        self.puuid = puuid
        self.name = name
        self.profile_icon_id = profileIconId
        self.revision_date = revisionDate
        self.summoner_level = summonerLevel

    def __repr__(self) -> str:
        return f"{self.name} <Level: {self.summoner_level}>"

    def __eq__(self, other) -> bool:
        return self.puuid == other.puuid

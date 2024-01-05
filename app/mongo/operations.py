import os

from pymongo import MongoClient

MONGO_DB_USER = os.environ.get("MONGO_INITDB_ROOT_USERNAME", "admin")
MONGO_DB_PASSWORD = os.environ.get("MONGO_INITDB_ROOT_PASSWORD", "adminpassword")
MONGO_DB_HOST = os.environ.get("MONGO_HOST", "localhost")
MONGO_DB_PORT = os.environ.get("MONGO_PORT", 27017)
MONGO_DB_NAME = os.environ.get("MONGO_INITDB_DATABASE", "lolanalytics")

MONGO_COLLECTION_NAME = "lol_matches"

MONGO_DB_URL = (
    f"mongodb://{MONGO_DB_USER}:{MONGO_DB_PASSWORD}@{MONGO_DB_HOST}:{MONGO_DB_PORT}"
)

client = MongoClient(MONGO_DB_URL)

db = client[MONGO_DB_NAME]


def insert_match_data(match_data: dict) -> None:
    db[MONGO_COLLECTION_NAME].insert_one(match_data)


def insert_many_matches_data(matches_data: list[dict]) -> None:
    db[MONGO_COLLECTION_NAME].insert_many(matches_data)


def find_match_by_id(match_id: str):
    return db[MONGO_COLLECTION_NAME].find_one(
        {"metadata.matchId": match_id}, {"_id": 0}
    )


def find_matches_by_ids(match_ids: list[str]):
    return db[MONGO_COLLECTION_NAME].find(
        {"metadata.matchId": {"$in": match_ids}}, {"_id": 0}
    )


def find_matches_by_puuid(puuid: str, datetimestamp: int = None) -> list[dict]:
    match_param = {"first_document.metadata.participants": {"$in": [puuid]}}
    if datetimestamp:
        match_param["first_document.info.gameCreation"] = {"$gt": datetimestamp}

    cursor = db[MONGO_COLLECTION_NAME].aggregate(
        [
            {
                "$group": {
                    "_id": "$metadata.matchId",
                    "first_document": {"$first": "$$ROOT"},
                }
            },
            {"$match": match_param},
            {
                "$project": {
                    "_id": 0,
                    "first_document.metadata.matchId": 1,
                    "first_document.metadata.participants": 1,
                    "first_document.info.gameCreation": 1,
                    "first_document.info.gameDuration": 1,
                    "first_document.info.gameEndTimestamp": 1,
                    "first_document.info.gameStartTimestamp": 1,
                    "first_document.info.gameMode": 1,
                    "first_document.info.participants.puuid": 1,
                    "first_document.info.participants.teamId": 1,
                    "first_document.info.participants.assists": 1,
                    "first_document.info.participants.deaths": 1,
                    "first_document.info.participants.kills": 1,
                    "first_document.info.participants.doubleKills": 1,
                    "first_document.info.participants.tripleKills": 1,
                    "first_document.info.participants.quadraKills": 1,
                    "first_document.info.participants.pentaKills": 1,
                    "first_document.info.participants.firstBloodKill": 1,
                    "first_document.info.participants.dragonKills": 1,
                    "first_document.info.participants.totalDamageDealt": 1,
                    "first_document.info.participants.totalDamageDealtToChampions": 1,
                    "first_document.info.participants.magicDamageDealt": 1,
                    "first_document.info.participants.magicDamageDealtToChampions": 1,
                    "first_document.info.participants.totalHealsOnTeammates": 1,
                    "first_document.info.participants.visionScore": 1,
                    "first_document.info.participants.goldEarned": 1,
                    "first_document.info.participants.goldSpent": 1,
                    "first_document.info.participants.turretTakedowns": 1,
                    "first_document.info.participants.wardsKilled": 1,
                    "first_document.info.participants.wardsPlaced": 1,
                    "first_document.info.participants.damageSelfMitigated": 1,
                    "first_document.info.participants.killingSprees": 1,
                    "first_document.info.participants.largestCriticalStrike": 1,
                    "first_document.info.participants.largestKillingSpree": 1,
                    "first_document.info.participants.objectivesStolen": 1,
                    "first_document.info.participants.totalMinionsKilled": 1,
                    "first_document.info.participants.totalTimeCCDealt": 1,
                    "first_document.info.participants.totalAllyJungleMinionsKilled": 1,
                    "first_document.info.participants.baronTakedowns": 1,
                    "first_document.info.participants.championName": 1,
                    "first_document.info.participants.championId": 1,
                    "first_document.info.participants.win": 1,
                    "first_document.info.participants.teamPosition": 1,
                    "first_document.info.participants.item0": 1,
                    "first_document.info.participants.item1": 1,
                    "first_document.info.participants.item2": 1,
                    "first_document.info.participants.item3": 1,
                    "first_document.info.participants.item4": 1,
                    "first_document.info.participants.item5": 1,
                    "first_document.info.participants.item6": 1,
                    "first_document.info.participants.challenges": 1,
                    "first_document.info.teams.objectives.kills": 1,
                    "first_document.info.teams.objectives.dragon": 1,
                    "first_document.info.teams.objectives.baron": 1,
                    "first_document.info.teams.teamId": 1,
                }
            },
        ]
    )

    return list(cursor)

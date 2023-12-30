import os

from pymongo import MongoClient

MONGO_DB_USER = os.environ.get("MONGO_INITDB_ROOT_USERNAME", "admin")
MONGO_DB_PASSWORD = os.environ.get(
    "MONGO_INITDB_ROOT_PASSWORD",
    "adminpassword"
    )
MONGO_DB_HOST = os.environ.get("MONGO_HOST", "localhost")
MONGO_DB_PORT = os.environ.get("MONGO_PORT", 27017)
MONGO_DB_NAME = os.environ.get("MONGO_INITDB_DATABASE", "lolanalytics")

MONGO_COLLECTION_NAME = "lol_matches"

MONGO_DB_URL = (
    f"mongodb://{MONGO_DB_USER}:{MONGO_DB_PASSWORD}@{MONGO_DB_HOST}:\
    {MONGO_DB_PORT}"
)

client = MongoClient(MONGO_DB_URL)

db = client[MONGO_DB_NAME]


def insert_match_data(match_data: dict) -> None:
    db[MONGO_COLLECTION_NAME].insert_one(match_data)


def insert_many_matches_data(matches_data: list[dict]):
    db[MONGO_COLLECTION_NAME].insert_many(matches_data)


def find_match_by_id(match_id: str):
    return db[MONGO_COLLECTION_NAME].find_one({"match_id": match_id})


def find_matches_by_ids(match_ids: list[str]):
    return db[MONGO_COLLECTION_NAME].find({"match_id": {"$in": match_ids}})


def find_matches_by_puuid(puuid: str):
    return db[MONGO_COLLECTION_NAME].find({"puuid": puuid})

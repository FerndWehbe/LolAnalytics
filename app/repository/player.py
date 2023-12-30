from database import dec_session_local
from models import Player
from sqlalchemy import text
from sqlalchemy.orm import Session


@dec_session_local
def create_player(db: Session, player: Player) -> Player:
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


@dec_session_local
def get_player(db: Session, player_puuid: str) -> Player:
    return db.query(Player).filter(Player.puuid == player_puuid).first()


@dec_session_local
def update_player(db: Session, player_puuid: str, updated_player: Player) -> Player:
    existing_item = db.query(Player).filter(Player.puuid == player_puuid).first()
    if existing_item:
        for key, value in updated_player.dict().items():
            setattr(existing_item, key, value)
        db.commit()
        db.refresh(existing_item)
    return existing_item


@dec_session_local
def get_player_by_name(db: Session, player_name: str) -> Player:
    return db.query(Player).filter(Player.name == player_name).first()


@dec_session_local
def get_matches_not_searched_by_puuid(db: Session, player_puuid: str) -> list[str]:
    sql_query = text(
        """
        SELECT m.match_id
        FROM "Player" p
        INNER JOIN "PlayerMatchAssociation" pma ON pma.player_puuid = p.puuid
        INNER JOIN "Match" m ON m.match_id = pma.match_id
        WHERE p.puuid = :puuid
        AND m.is_searched = false
    """
    )

    params = {"puuid": player_puuid}

    result = db.execute(sql_query, params)

    return [match[0] for match in result.fetchall()]

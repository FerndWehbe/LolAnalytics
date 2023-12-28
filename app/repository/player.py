from database import SessionLocal, dec_session_local
from models import Player


@dec_session_local
def create_player(db: SessionLocal, player: Player) -> Player:
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


@dec_session_local
def get_player(db: SessionLocal, player_puuid: str) -> Player:
    return db.query(Player).filter(Player.puuid == player_puuid).first()


@dec_session_local
def update_player(
    db: SessionLocal, player_puuid: str, updated_player: Player
) -> Player:
    existing_item = db.query(Player).filter(Player.puuid == player_puuid).first()
    if existing_item:
        for key, value in updated_player.dict().items():
            setattr(existing_item, key, value)
        db.commit()
        db.refresh(existing_item)
    return existing_item


@dec_session_local
def get_player_by_name(db: SessionLocal, player_name: str) -> Player:
    return db.query(Player).filter(Player.name == player_name).first()

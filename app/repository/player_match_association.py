from database import SessionLocal, dec_session_local
from models import PlayerMatchAssociation


@dec_session_local
def create_player_match_association(
    db: SessionLocal, player_match: PlayerMatchAssociation
):
    db.add(player_match)
    db.commit()
    db.refresh(player_match)
    return player_match

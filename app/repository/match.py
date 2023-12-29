from database import SessionLocal, dec_session_local
from models import Match


@dec_session_local
def create_match(db: SessionLocal, match: Match) -> Match:
    db.add(match)
    db.commit()
    db.refresh(match)
    return match

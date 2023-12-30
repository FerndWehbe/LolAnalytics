from database import SessionLocal, dec_session_local
from models import Match


@dec_session_local
def create_match(db: SessionLocal, match: Match) -> Match:
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


@dec_session_local
def get_match(db: SessionLocal, match_id: str) -> Match:
    return db.query(Match).filter(Match.match_id == match_id).first()


@dec_session_local
def update_match(db: SessionLocal, match_id: str, updated_match: Match) -> Match:
    existing_match = db.query(Match).filter(Match.match_id == match_id).first()
    if existing_match:
        for key, value in updated_match.to_dict().items():
            setattr(existing_match, key, value)
        db.commit()
        db.refresh(existing_match)
    return existing_match

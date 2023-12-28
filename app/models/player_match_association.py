from database import Base
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship


class PlayerMatchAssociation(Base):
    __tablename__ = "PlayerMatchAssociation"

    id = Column(String, primary_key=True)
    player_puuid = Column(String, ForeignKey("Player.puuid"))
    match_id = Column(String, ForeignKey("Match.match_id"))

    player = relationship("Player", back_populates="matches")
    match = relationship("Match", back_populates="players")

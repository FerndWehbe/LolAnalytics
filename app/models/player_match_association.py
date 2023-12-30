from database import Base
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship


class PlayerMatchAssociation(Base):
    __tablename__ = "PlayerMatchAssociation"

    player_puuid = Column(String, ForeignKey("Player.puuid"), primary_key=True)
    match_id = Column(String, ForeignKey("Match.match_id"), primary_key=True)

    player = relationship("Player", back_populates="matches")
    match = relationship("Match", back_populates="players")

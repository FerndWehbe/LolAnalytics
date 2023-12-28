from database import Base
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship


class Player(Base):
    __tablename__ = "Player"
    puuid = Column(String, primary_key=True, unique=True)
    name = Column(String)
    riot_id = Column(String)
    update = Column(DateTime)
    rewind_id = Column(DateTime)

    matches = relationship("PlayerMatchAssociation", back_populates="player")

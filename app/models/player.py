from database import Base
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship


class Player(Base):
    __tablename__ = "Player"
    puuid = Column(String, primary_key=True, unique=True)
    summoner_id = Column(String)
    name = Column(String)
    riot_id = Column(String)
    region = Column(String)
    update = Column(DateTime)
    rewind_id = Column(String)

    matches = relationship(
        "PlayerMatchAssociation", back_populates="player", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "puuid": self.puuid,
            "name": self.name,
            "region": self.region,
            "riot_id": self.riot_id,
            "update": self.update,
            "rewind_id": self.rewind_id,
        }

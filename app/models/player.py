from database import Base
from sqlalchemy import Column, DateTime, String


class Player(Base):
    __tablename__ = "Player"
    puuid = Column(String, primary_key=True)
    name = Column(String)
    riot_id = Column(String)
    update = Column(DateTime)
    rewind_id = Column(DateTime)

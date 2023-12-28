from database import Base
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship


class Match(Base):
    __tablename__ = "Match"
    match_id = Column(String, primary_key=True)
    is_searched = Column(Boolean, default=False)

    players = relationship("PlayerMatchAssociation", back_populates="match")

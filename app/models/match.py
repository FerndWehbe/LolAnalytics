from database import Base
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship


class Match(Base):
    __tablename__ = "Match"
    match_id = Column(String, primary_key=True)
    is_searched = Column(Boolean, default=False)

    players = relationship("PlayerMatchAssociation", back_populates="match")

    def to_dict(self):
        return {"match_id": self.match_id, "is_searched": self.is_searched}

from database import Base
from sqlalchemy import Boolean, Column, String


class Match(Base):
    __tablename__ = "Match"
    match_id = Column(String, primary_key=True)
    is_searched = Column(Boolean)

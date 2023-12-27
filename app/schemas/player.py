from datetime import datetime

from pydantic import BaseModel


class Player(BaseModel):
    puuid: str
    name: str
    riot_id: str
    update: datetime
    rewind_id: datetime

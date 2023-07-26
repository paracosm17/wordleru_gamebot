from uuid import uuid4

from sqlalchemy import Column, Integer, BigInteger, Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from tgbot.database.base import Base


class GameHistoryEntry(Base):
    __tablename__ = "gameshistory"

    game_id = Column(Text(length=36), default=lambda: str(uuid4()), primary_key=True)
    played_at = Column(DateTime, nullable=False)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    answer = Column(String, nullable=False)
    attempts = Column(Integer, nullable=False)
    victory = Column(Boolean, nullable=False)
    length = Column(Integer, nullable=False)

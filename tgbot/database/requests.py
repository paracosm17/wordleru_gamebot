from uuid import uuid4

from contextlib import suppress
from datetime import datetime
from typing import List, Dict

from sqlalchemy import select, distinct
from sqlalchemy.exc import IntegrityError

from tgbot.database.models import GameHistoryEntry


async def get_games_by_id(session_pool, user_id: int) -> List[GameHistoryEntry]:
    """
    Get game history for user

    :param session_pool: SQLAlchemy DB session
    :param user_id: player's Telegram ID
    :return: list of GameHistoryEntry objects
    """
    async with session_pool() as session:
        game_data_request = await session.execute(
            select(GameHistoryEntry).where(GameHistoryEntry.telegram_id == user_id)
        )
        return game_data_request.scalars().all()


async def get_bot_users(session_pool) -> List[GameHistoryEntry]:
    """
    Get bot users

    :param session_pool: SQLAlchemy DB session
    :return: list of GameHistoryEntry objects with unique telegram_id
    """
    async with session_pool() as session:
        users = await session.execute(
            select(distinct(GameHistoryEntry.telegram_id))
        )
        return users.scalars().all()


async def get_all_games(session_pool) -> List[GameHistoryEntry]:
    """
    Get all games

    :param session_pool: SQLAlchemy DB session
    :return: list of GameHistoryEntry objects
    """
    async with session_pool() as session:
        games = await session.execute(select(GameHistoryEntry))
        return games.scalars().all()


async def log_game(session_pool, data: Dict, telegram_id: int, win: bool):
    """
    Send end game event to database

    :param session_pool: SQLAlchemy DB session
    :param data: game data dictionary (only size is taken for now)
    :param telegram_id: Player's Telegram ID
    :param win: win or not win
    """
    async with session_pool() as session:
        entry = GameHistoryEntry()
        entry.game_id = str(uuid4())
        entry.played_at = datetime.utcnow()
        entry.telegram_id = telegram_id
        entry.attempts = len(data["used_words"])
        entry.answer = data["answer"]
        entry.victory = win
        entry.length = data["word_length"]
        session.add(entry)
        with suppress(IntegrityError):
            await session.commit()

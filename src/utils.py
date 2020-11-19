import os
import sys

import aioredis
from loguru import logger

_DB_CONNECTION: aioredis.Redis = None
_DB_CONNECTION_QUESTIONS: aioredis.Redis = None


async def get_questions_db_connection(db_id=1) -> aioredis.Redis:
    global _DB_CONNECTION_QUESTIONS

    if not _DB_CONNECTION_QUESTIONS or _DB_CONNECTION_QUESTIONS.closed:
        _DB_CONNECTION_QUESTIONS = await aioredis.create_redis_pool(
            address=(
                os.getenv("REDIS_HOST", "localhost"),
                os.getenv("REDIS_PORT", 6379),
            ),
            encoding="utf8",
            db=db_id,
        )

    return _DB_CONNECTION_QUESTIONS


async def get_db_connection() -> aioredis.Redis:
    global _DB_CONNECTION

    if not _DB_CONNECTION or _DB_CONNECTION.closed:
        _DB_CONNECTION = await aioredis.create_redis_pool(
            address=(
                os.getenv("REDIS_HOST", "localhost"),
                os.getenv("REDIS_PORT", 6379),
            ),
            encoding="utf8",
        )

    return _DB_CONNECTION


async def close_all_db_connections():
    global _DB_CONNECTION, _DB_CONNECTION_QUESTIONS

    if _DB_CONNECTION and not _DB_CONNECTION.closed:
        _DB_CONNECTION.close()
        await _DB_CONNECTION.wait_closed()

    if _DB_CONNECTION_QUESTIONS and not _DB_CONNECTION_QUESTIONS.closed:
        _DB_CONNECTION_QUESTIONS.close()
        await _DB_CONNECTION_QUESTIONS.wait_closed()


def get_logger_conf(log_level=os.getenv("LOG_LEVEL", "DEBUG")):
    return {
        "handlers": [
            {
                "sink": sys.stdout,
                "level": log_level,
                "format": "<level>{level: <8}</level>|<cyan>{name:<12}</cyan>:<cyan>{function:<24}</cyan>:<cyan>{line}</cyan> - <level>{message:>32}</level> |{extra}",
            },
        ],
    }

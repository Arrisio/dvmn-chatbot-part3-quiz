import asyncio
import os
import sys
from contextlib import asynccontextmanager

import aioredis
from loguru import logger

QUESTIONS_DB_ID = 1
#
# redis_questions_connection = None
# redis_quiz_connection = None
#
#
# async def init_redis_connections():
#     global redis_quiz_connection
#     global redis_questions_connection
#
#     r1 = await aioredis.create_redis_pool(
#         address=(
#             os.getenv("REDIS_HOST", "localhost"),
#             os.getenv("REDIS_PORT", 6379),
#         ),
#         db=QUESTIONS_DB_ID,
#         encoding="utf8",
#     )
#
#     r2 = await aioredis.create_redis_pool(
#         address=(
#             os.getenv("REDIS_HOST", "localhost"),
#             os.getenv("REDIS_PORT", 6379),
#         ),
#         encoding="utf8",
#     )
#
#     redis_questions_connection=r1
#     redis_quiz_connection=r2
#
#
# async def get_redis_qestion()

@asynccontextmanager
async def redis_ctx_connection(
    host: str = os.getenv("REDIS_HOST", "localhost"),
    port: int = os.getenv("REDIS_PORT", 6379),
    db: int = 0,
) -> aioredis.connection:
    logger.debug(
        "trying to connect to redis", extra={"host": host, "port": port, "db": db}
    )
    try:
        redis = await aioredis.create_redis_pool(
            address=(host, port),
            db=db,
            encoding="utf8",
        )

        logger.debug("redis connected successfilly", extra={"redis": redis.__repr__()})
    except ConnectionRefusedError:
        logger.error(
            "cannot connect to specified redis server",
            extra={"host": host, "port": port, "db": db},
        )
        raise
    try:
        yield redis

    finally:
        redis.close()
        await redis.wait_closed()


def get_logger_conf(log_level=os.getenv("LOG_LEVEL", "DEBUG")):
    return {
        "handlers": [
            {
                "sink": sys.stdout,
                "level": log_level,
                "format": "<level>{level: <8}</level>|<cyan>{name:<12}</cyan>:<cyan>{function:<24}</cyan>:<cyan>{line}</cyan> - <level>{message:>32}</level> |{extra}",
                "filter": lambda record: record["level"].no != logger.level("INFO").no,
            },
            {
                "sink": sys.stdout,
                "level": "INFO",
                "format": "<level>{level: <8}</level><level>{message:>32}</level>",
                "filter": lambda record: record["level"].no == logger.level("INFO").no,
            },
        ],
    }

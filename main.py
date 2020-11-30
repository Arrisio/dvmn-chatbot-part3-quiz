import asyncio

import asyncclick as click
from loguru import logger

from src.init_questions import init_questions
from src.tg import run_tg_bot
from src.utils import (
    get_logger_conf,
    close_all_db_connections,
)
# from src.vk import run_vk_bot

# async def runner()

@click.command()
@click.argument(
    "bot",
    type=click.Choice(["tg", "vk"]),
    default="tg",
)
async def main(bot):
    logger.configure(**get_logger_conf())
    # loop = asyncio.get_event_loop()

    # loop.run_until_complete()
    # await init_questions()
    if bot == "tg":
        await run_tg_bot()
    # elif bot == "vk":
    #     loop.run_until_complete(run_vk_bot())
    else:
        logger.error("incorrect bot option")

    # loop.run_until_complete(close_all_db_connections())


if __name__ == "__main__":
    asyncio.run(main())

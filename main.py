import pickle
from loguru import logger
from src.init_questions import init_questions
from src.utils import get_logger_conf
from src.tg import run_tg_bot
from src.vk import run_vk_bot
import asyncio
import click


@click.command()
@click.argument(
    "bot",
    type=click.Choice(["tg", "vk"]),
    default="vk",
)
def main(bot):
    logger.configure(**get_logger_conf())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_questions())
    if bot == "tg":
        run_tg_bot(loop=loop)
    elif bot == "vk":
        loop.run_until_complete(run_vk_bot())
    else:
        logger.error("incorrect bot option")


if __name__ == "__main__":
    main()

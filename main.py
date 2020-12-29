import asyncio

import click
from loguru import logger

from src.init_questions import init_questions, check_question_db_empty
from src.tg import run_tg_bot
from src.utils import get_logger_conf, close_all_db_connections
from src.vk import run_vk_bot


@click.command()
@click.argument(
    "bot",
    type=click.Choice(["tg", "vk"]),
    default="vk",
)
@click.option("-r", "--reload", is_flag=True, help="force reload quize questions")
@click.option(
    "-u",
    "--questions-url",
    "url",
    default="http://dvmn.org/media/modules_dist/quiz-questions.zip",
    show_default=True,
    help="url for downloading questions",
)
def main(bot, reload, url):

    logger.configure(**get_logger_conf())

    loop = asyncio.get_event_loop()
    # использование run_until_complete соласовано в телеге
    # Т.е. при asyncio.run  лезут ошибки при запуске aiogram
    is_question_db_empty = loop.run_until_complete(check_question_db_empty())
    if reload or is_question_db_empty:
        loop.run_until_complete(init_questions(url))

    # asyncio.run(init_questions())
    if bot == "tg":
        run_tg_bot(loop)
    elif bot == "vk":
        loop.run_until_complete(run_vk_bot())
    else:
        logger.error("incorrect bot option")

    loop.run_until_complete(close_all_db_connections())


if __name__ == "__main__":
    # asyncio.run(main())
    main()

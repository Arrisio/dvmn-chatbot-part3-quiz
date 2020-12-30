import asyncio
import os
import re
import zipfile

import anyio
import requests
from loguru import logger
from tqdm import tqdm

from src.utils import (
    get_logger_conf,
    get_questions_db_connection,
    close_all_db_connections,
)


def download_file(
    url,
    filename: str,
    chunk_size: int = 1024,
):
    """Helper method handling downloading large files from `url` to `filename`."""
    r = requests.get(url, stream=True)
    logger.info("start downloading questions archive")
    with open(filename, "wb") as f:
        pbar = tqdm(unit="B", total=int(r.headers["Content-Length"]))
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:  # filter out keep-alive new chunks
                pbar.update(len(chunk))
                f.write(chunk)


async def check_question_db_empty():
    return await (await get_questions_db_connection()).dbsize() == 0


def extract_qnas_from_zip(archive_path: str):
    pattern = re.compile(r"Вопрос\s+\d+:\n(.*?)[\n]+Ответ:\n+(.*?)\.\n", flags=re.S)

    with zipfile.ZipFile(archive_path) as zip_handler:
        logger.info("start converting questions archive")
        for question_file_name in tqdm(zip_handler.namelist()):
            with zip_handler.open(question_file_name) as question_file_name_handler:
                file_text = question_file_name_handler.read().decode("koi8-r")
                for question, answer in pattern.findall(file_text):
                    yield question, answer


async def init_questions(
    questions_url="http://127.0.0.1:8000/quiz-questions.zip",
) -> None:
    logger.info("start downloading questions")
    redis = await get_questions_db_connection()

    tmp_quiz_filename = "quiz-questions2.zip"  # не используется библиотека tempfile, т.к. для корректной работы на винде треуебтся слишком много приседаний
    try:
        download_file(
            url=questions_url,
            filename=tmp_quiz_filename,
        )

        async with anyio.create_task_group() as tg:
            for q, a in extract_qnas_from_zip(tmp_quiz_filename):
                await tg.spawn(redis.set, q, a)

    finally:
        os.remove(tmp_quiz_filename)

    logger.info("questions are ready")


async def main():
    logger.configure(**get_logger_conf())
    await init_questions()
    await close_all_db_connections()


if __name__ == "__main__":
    asyncio.run(main())

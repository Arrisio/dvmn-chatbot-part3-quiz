import asyncio
import re
import zipfile

import requests
from loguru import logger
from tqdm import tqdm

from src.utils import get_logger_conf, get_questions_db_connection, close_all_db_connections


def download_file(url, filename: str, chunk_size: int = 1024):
    """
    Helper method handling downloading large files from `url` to `filename`.
    """

    r = requests.get(url, stream=True)
    logger.info("start downloading questions archive")
    with open(filename, "wb") as f:
        pbar = tqdm(unit="B", total=int(r.headers["Content-Length"]))
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:  # filter out keep-alive new chunks
                pbar.update(len(chunk))
                f.write(chunk)


def extract_question_and_answer(
    question_text_block: str,
    question_pattern=re.compile(r"Вопрос \d{1,4}:\n(.*)", flags=re.DOTALL),
    answer_pattern=re.compile(r"Ответ:\n(.*)", flags=re.DOTALL),
):
    question = answer = None
    for block_part in question_text_block.split("\n\n"):
        if questions := question_pattern.findall(block_part):
            question = questions[0]
        if answers := answer_pattern.findall(block_part):
            answer = answers[0].split(".")[0].lower()
    if question and answer:
        return question, answer


def fetch_qnas(archive_path):
    pattern = re.compile(r"Вопрос\s+\d+:\n(.*?)[\n]+Ответ:\n+(.*?)\.\n", flags=re.S)

    with zipfile.ZipFile(archive_path) as zip_handler:
        logger.info("start converting questions archive")
        for question_file_name in tqdm(zip_handler.namelist()):
            with zip_handler.open(question_file_name) as question_file_name_handler:
                file_text = question_file_name_handler.read().decode("koi8-r")
                for question, answer in pattern.findall(file_text):
                    yield question, answer
                    return


async def init_questions(
    questions_archive_url="http://dvmn.org/media/modules_dist/quiz-questions.zip",
) -> None:

    redis = await get_questions_db_connection()

    if await redis.dbsize() > 0:
        logger.info("questions are ready")
        return

    tmp_quiz_filename = "quiz-questions.zip"
    logger.debug(tmp_quiz_filename)
    download_file(
        url=questions_archive_url,
        filename=tmp_quiz_filename,
    )

    await asyncio.wait([redis.set(q, a) for q, a in fetch_qnas(tmp_quiz_filename)])

    os.remove(tmp_quiz_filename)
    logger.info("questions are ready")


if __name__ == "__main__":
    logger.configure(**get_logger_conf())
    loop = asyncio.get_event_loop()

    loop.run_until_complete(init_questions())
    loop.run_until_complete(close_all_db_connections())


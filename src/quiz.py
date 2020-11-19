from enum import Enum

from loguru import logger

from src.utils import get_db_connection, get_questions_db_connection
from typing import List


async def if_question_asked(user_id: str) -> bool:
    db = await get_db_connection()
    return await db.exists(user_id) == 1


async def ask_question(user_id: str) -> str:
    db = await get_db_connection()
    questions_db= await get_questions_db_connection()

    question = await questions_db.randomkey()
    logger.debug('asking question', extra={'question':question, 'answer': await questions_db.get(question)})
    await db.set(user_id, question)
    return question


async def verify_answer(user_id: str, answer: str) -> bool:
    db = await get_db_connection()
    questions_db= await get_questions_db_connection()

    question = await db.get(user_id)
    correct_answer = await questions_db.get(key=question)
    return correct_answer.lower() == answer.lower()


async def give_up(user_id: str) -> List[str]:
    """
    :param user_id: tg or vk user_id , for example "tg-673451"
    :return: messages list
    """
    db = await get_db_connection()
    questions_db= await get_questions_db_connection()

    if asked_question := await db.get(user_id):
        correct_answer = await questions_db.get(asked_question)
        new_question = await ask_question(user_id)

        return [correct_answer, new_question]

    else:
        return ["Рано сдаваться. ничего  еще не спросили!"]


class Buttons(Enum):
    NEW_QUESTION = "Новый вопрос"
    GIVE_UP = "Сдаться"
    MY_SCORE = "Мой счет"
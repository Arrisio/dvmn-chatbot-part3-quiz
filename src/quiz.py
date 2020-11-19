from enum import Enum

from loguru import logger

from src.utils import redis_ctx_connection, QUESTIONS_DB_ID
from typing import List


async def if_question_asked(user_id: str) -> bool:
    async with redis_ctx_connection() as redis_quiz_connection:
        return await redis_quiz_connection.exists(user_id) == 1


async def ask_question(user_id: str) -> str:
    async with redis_ctx_connection() as redis_quiz_connection:
        async with redis_ctx_connection(db=QUESTIONS_DB_ID) as redis_questions_connection:
            question = await redis_questions_connection.randomkey()
            logger.debug('asking question', extra={'question':question, 'answer': await redis_questions_connection.get(question)})
            await redis_quiz_connection.set(user_id, question)
            return question


async def verify_answer(user_id: str, answer: str) -> bool:
    async with redis_ctx_connection() as redis_quiz_connection:
        async with redis_ctx_connection(db=QUESTIONS_DB_ID) as redis_questions_connection:
            question = await redis_quiz_connection.get(user_id)
            correct_answer = await redis_questions_connection.get(key=question)
            return correct_answer.lower() == answer.lower()


async def give_up(user_id: str) -> List[str]:
    """
    :param user_id: tg or vk user_id , for example "tg-673451"
    :return: messages list
    """
    async with redis_ctx_connection() as redis_quiz_connection:
        async with redis_ctx_connection(db=QUESTIONS_DB_ID) as redis_questions_connection:
            if asked_question := await redis_quiz_connection.get(user_id):
                correct_answer = await redis_questions_connection.get(asked_question)
                new_question = await ask_question(user_id)

                return [correct_answer, new_question]

            else:
                return ["Рано сдаваться. ничего  еще не спросили!"]


class Buttons(Enum):
    NEW_QUESTION = "Новый вопрос"
    GIVE_UP = "Сдаться"
    MY_SCORE = "Мой счет"
from enum import Enum

from loguru import logger

from src.utils import get_quiz_state_db_connection, get_questions_db_connection


async def check_if_question_asked(user_id: str) -> bool:
    quiz_state_db = await get_quiz_state_db_connection()

    return await quiz_state_db.exists(user_id) == 1


async def ask_question(user_id: str) -> str:
    quiz_state_db = await get_quiz_state_db_connection()
    questions_db = await get_questions_db_connection()

    question = await questions_db.randomkey()
    logger.debug(
        "asking question",
        extra={"question": question, "answer": await questions_db.get(question)},
    )
    await quiz_state_db.set(user_id, question)

    return question


async def verify_answer(user_id: str, answer: str) -> bool:
    quiz_state_db = await get_quiz_state_db_connection()
    questions_db = await get_questions_db_connection()

    question = await quiz_state_db.get(user_id)
    correct_answer = await questions_db.get(key=question)

    return correct_answer.lower() == answer.lower()


async def get_answer_to_asked_question(user_id: str) -> str:
    quiz_state_db = await get_quiz_state_db_connection()
    questions_db = await get_questions_db_connection()
    if asked_question := await quiz_state_db.get(user_id):
        return await questions_db.get(asked_question)


class Buttons(Enum):
    NEW_QUESTION = "Новый вопрос"
    GIVE_UP = "Сдаться"
    MY_SCORE = "Мой счет"

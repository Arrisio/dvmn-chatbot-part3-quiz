from enum import Enum

from loguru import logger

# from src.utils import question_db_ctx,quiz_state_db_ctx
from src.utils import get_quiz_state_db_connection,get_questions_db_connection
from typing import List


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



# использование названия give_up обсуждали в телеге
# т.е. ответа я так и не получил - пока оставляю свой вариант
async def give_up(user_id: str) -> List[str]:
    """
    Обрабатывает бизнес-сценарий сдачи пользователя.
    Args:
        user_id:

    Returns:
        возвращается правильный ответ и новый вопрос.
    """


    quiz_state_db = await get_quiz_state_db_connection()
    questions_db = await get_questions_db_connection()

    if asked_question := await quiz_state_db.get(user_id):
        correct_answer = await questions_db.get(asked_question)
        new_question = await ask_question(user_id)

        return [correct_answer, new_question]

    else:
        return ["Рано сдаваться. ничего  еще не спросили!"]


class Buttons(Enum):
    NEW_QUESTION = "Новый вопрос"
    GIVE_UP = "Сдаться"
    MY_SCORE = "Мой счет"

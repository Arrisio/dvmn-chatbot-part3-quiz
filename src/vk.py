import os
import random
from typing import Generator

import anyio
import vk_api
from loguru import logger
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from src import quiz

keyboard = VkKeyboard(one_time=True)
keyboard.add_button(quiz.Buttons.NEW_QUESTION.value, color=VkKeyboardColor.PRIMARY)
keyboard.add_button(quiz.Buttons.GIVE_UP.value, color=VkKeyboardColor.NEGATIVE)
keyboard.add_line()
keyboard.add_button(quiz.Buttons.MY_SCORE.value, color=VkKeyboardColor.PRIMARY)


async def process_message(event, vk):
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        logger.debug(
            "Income message",
            extra={"user_id": event.user_id, "text": event.text},
        )

        if event.text == quiz.Buttons.NEW_QUESTION.value:
            question = await quiz.ask_question(f"vk-{event.user_id}")
            vk.messages.send(
                user_id=event.user_id,
                message=question,
                keyboard=keyboard.get_keyboard(),
                random_id=random.randint(1, 1000),
            )
        elif event.text == quiz.Buttons.GIVE_UP.value:
            messages = await quiz.give_up(f"vk-{event.user_id}")
            for message in messages:
                vk.messages.send(
                    user_id=event.user_id,
                    message=message,
                    keyboard=keyboard.get_keyboard(),
                    random_id=random.randint(1, 1000),
                )
        elif event.text == quiz.Buttons.MY_SCORE.value:
            vk.messages.send(
                user_id=event.user_id,
                message="Точно не знаю, но видали и получше",
                keyboard=keyboard.get_keyboard(),
                random_id=random.randint(1, 1000),
            )
        elif await quiz.check_if_question_asked(f"vk-{event.user_id}"):
            if await quiz.verify_answer(user_id=f"vk-{event.user_id}", answer=event.text):
                vk.messages.send(
                    user_id=event.user_id,
                    message="Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»",
                    keyboard=keyboard.get_keyboard(),
                    random_id=random.randint(1, 1000),
                )
            else:
                vk.messages.send(
                    user_id=event.user_id,
                    message="Неправильно... Попробуешь ещё раз?",
                    keyboard=keyboard.get_keyboard(),
                    random_id=random.randint(1, 1000),
                )
        else:
            vk.messages.send(
                user_id=event.user_id,
                message='Нажмите "Новый вопрос" чтоб запустить викторину',
                keyboard=keyboard.get_keyboard(),
                random_id=random.randint(1, 1000),
            )


def get_next_vk_event_from_listener(vk_listener: Generator) -> VkEventType:
    """Обертка над синхронным генератором, чтоб весь текущий модуль по обработке vk-ивентов мог работать асинхронно.

    Args:
        vk_listener: генератор vk_api.longpoll.VkLongPoll().listen()

    Returns:
        vk_api.longpoll.VkEventType: Перечисление событий, получаемых от longpoll-сервера.
    """
    return vk_listener.send(None)


async def run_vk_bot():
    logger.info("vk bot started")
    try:
        vk_session = vk_api.VkApi(token=os.environ["VK_TOKEN"])
        longpoll = VkLongPoll(vk=vk_session)
        vk = vk_session.get_api()
        vk_listener = longpoll.listen()

        while True:
            event = await anyio.run_sync_in_worker_thread(get_next_vk_event_from_listener, vk_listener)
            async with anyio.create_task_group() as tg:
                await tg.spawn(process_message, event, vk)

    except (KeyboardInterrupt, SystemExit) as err:
        logger.info(f"shutting down.. {err}")
        raise

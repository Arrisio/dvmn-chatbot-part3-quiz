import asyncio
import logging
import os

from aiogram import Dispatcher, Bot, types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from loguru import logger

from src import quiz
from src.quiz import Buttons

loop = asyncio.get_event_loop()
bot = Bot(token=os.environ["TG_BOT_TOKEN"], parse_mode=types.ParseMode.HTML, loop=loop)
dp = Dispatcher(bot)


class IsQuestionAsked(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return await quiz.check_if_question_asked(f"tg-{message.from_user.id}")


def setup(dp: Dispatcher):
    dp.filters_factory.bind(IsQuestionAsked)


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=Buttons.NEW_QUESTION.value),
            KeyboardButton(text=Buttons.GIVE_UP.value),
        ],
        [KeyboardButton(text=Buttons.MY_SCORE.value)],
    ],
    resize_keyboard=True,
)


@dp.message_handler(CommandStart())
async def reply_start_command(message: types.Message):
    logging.debug("bot_start")
    await message.answer(f'you entered "start" command', reply_markup=keyboard)


@dp.message_handler(text=Buttons.NEW_QUESTION.value)
async def ask_new_question(message: types.Message):
    logging.debug("ask_new_question")
    await message.answer(await quiz.ask_question(user_id=f"tg-{message.from_user.id}"))


@dp.message_handler(text=Buttons.GIVE_UP.value)
async def give_up(message: types.Message):
    logging.debug("give_ip")
    for response_message in await quiz.give_up(user_id=f"tg-{message.from_user.id}"):
        await message.answer(response_message)


@dp.message_handler(text=Buttons.MY_SCORE.value)
async def get_score(message: types.Message):
    logging.debug("get_score")
    await message.answer("Точно не знаю, но видали и получше")


@dp.message_handler(IsQuestionAsked())
async def verify_answer(message: types.Message):
    logging.debug("verify_answer")

    if await quiz.verify_answer(user_id=f"tg-{message.from_user.id}", answer=message.text):
        await message.answer("Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»")
    else:
        await message.answer("Неправильно... Попробуешь ещё раз?")


@dp.message_handler()
async def reply_by_default(message: types.Message):
    logging.debug("default_answer")
    await message.answer('Нажмите "Новый вопрос" чтоб запустить викторину')


# >    По поводу замечания 26 "Код можно заметно упростить, упаковав всё в один асинхронный контекстный менеджер как это делалось в модуле по асинхронному Python"
# Обсуждали это в телеге, ответ проверяющего
# >ХЗ как это обойти. Видимо, придётся смириться и подстроиться.
# >Ну или запустить это добро в отдельном потоке.
# Но т.к. использьзуются глобальные переменные, то идея с отдельным потоком не катит


def run_tg_bot(loop):
    logger.info("telegram service started")
    executor.start_polling(dp, loop=loop)
    logger.info("service service stopped")

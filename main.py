# import aiogram
# import logging
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
#
#
# token = '5532876387:AAGKhiyMgftIJmHgPDhQLBb5GciXWCk7FEA'
# logging.basicConfig(level=logging.INFO)
# bot = aiogram.Bot(token=token)
# storage = MemoryStorage()
# dp = aiogram.Dispatcher(bot, storage=storage)
#
#
# @dp.message_handler()
# async def e(message: aiogram.types.Message):
#     await bot.send_message(message.chat.id, message.text)
#
#
# if __name__ == '__main__':
#     aiogram.executor.start_polling(dp, skip_updates=True)

import os
import datetime
import logging
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot_config import API_KEY

logging.basicConfig(level=logging.INFO)

TOKEN = API_KEY

bot = Bot(token=API_KEY)

# Initializing a memory storage
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States initialization
class Case(StatesGroup):
    text = State()
    date = State()
    time = State()


@dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    """
    Conversation's entry point
    """
    await bot.send_message(message.chat.id, ('Hello, {user}').format(user=message.from_user.full_name))

    # Configure ReplyKeyboardMarkup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True)
    markup.add("Remind me", "Exit")
    await bot.send_message(message.chat.id, "What can i do for ya?", reply_markup=markup)


# @dp.message_handler()
# async def echo(message: types.Message):
#     """Echo function"""
#     # await bot.send_message(message.message_id, message.text)
#     # await bot.send_message(message.chat.id, message.text)
#     await message.answer(message.text)


@dp.message_handler(commands=['test'])
async def comm_gleb(message: types.Message):
    """
    Command to test the bot state
    """
    await bot.send_message(message.chat.id, "The state is normal")


@dp.message_handler(lambda message: message.text in ["Remind me"])
async def cmd_case(message: types.Message):
    """
    Asks the user about his case
    """
    # Set case
    await Case.text.set()

    await message.reply("What's your plan?")


@dp.message_handler(state=Case.text)
async def process_case_text(message: types.Message, state: FSMContext):
    """
    Process the case text
    """
    async with state.proxy() as data:
        data['text'] = message.text

        await Case.next()

        # await message.reply('Okay, now choose the date for your plan\n(type the date in format "YYYY-MM-DD")')

        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Okay,'),
                md.text('now - choose the date for your plan'),
                md.bold('(type the date in format YYYY-MM-DD)'),
                md.text('for example: 2022-12-31'),
                sep='\n',
            ),
            parse_mode=ParseMode.MARKDOWN,
        )


@dp.message_handler(state=Case.date)
async def process_case_text(message: types.Message, state: FSMContext):
    """
    Processes the case date
    """
    async with state.proxy() as data:
        data['date'] = message.text

        await Case.next()

        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Almost completed,'),
                md.text('now - choose the time for your plan'),
                md.text(md.bold('(type the time in format "HH:MM:SS")')),
                md.text('for example: 12:00:00'),
                sep='\n',
            )
        )


@dp.message_handler(state=Case.time)
async def process_case_tho(message: types.Message, state: FSMContext):
    """
    Processes the case time and finishes the case state
    """
    async with state.proxy() as data:
        data['time'] = message.text

        markup = types.ReplyKeyboardRemove()

        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Plan:', md.bold(data['text'])),
                md.text(data['date'], ' - ', data['time']),
                md.text("I'll remind you about it in time!"),
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )

    await state.finish()


@dp.message_handler()
async def case_remind(message: types.Message):
    """
    Remind function
    """
    if Case.date == datetime.datetime.today():
        if Case.time == datetime.datetime.now():
            await bot.send_message(message.chat.id, 'REMIND!:\n{casetext}'.format(casetext=Case.text))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)



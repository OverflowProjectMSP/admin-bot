import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.storage.memory import MemoryStorage
import psycopg2
import logging
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y—%m—%d %H:%M:%S",
)

PASSWORD_PG = os.getenv('PASSWORD_PG')
PORT_PG = os.getenv('PORT_PG')
USER_PG = os.getenv('USER_PG')
HOST_PG = os.getenv('HOST_PG')
TOKEN = os.getenv('TOKEN')
PASSWORD = os.getenv('PASSWORD')

storage = MemoryStorage()
bot = Bot(token=TOKEN, storage=storage)

dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"Hello, {message.from_user.first_name}")

@dp.message(Command("login"))
async def login(message: types.Message):
    print(message.text)
    if message.text == PASSWORD:
        await storage.set_data(chat=message.chat.id, data={'id': message.from_user.id})
    else: await message.answer("Неверный пароль!")

@dp.message(Command("check"))
async def chech(message: types.Message):
    data = storage.get_data(message.from_chat.id)
    if data is None:
        await message.answer("Ты не в аккаунте")
    else:
        await message.answer("Ты в аккаунте")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
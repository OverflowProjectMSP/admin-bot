import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm.storage.memory import MemoryStorage
import psycopg2
from psycopg2 import extras, Error
import logging
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import datetime

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y—%m—%d %H:%M:%S",
)

PASSWORD_PG = os.getenv('DB_PASSWORD')
PORT_PG = os.getenv('DB_PORT')
USER_PG = os.getenv('DB_USERNAME')
HOST_PG = os.getenv('DB_HOST')
TOKEN = os.getenv('TOKEN')
PASSWORD = os.getenv('DB_PASSWORD')
IDS = os.getenv('IDS').split(',')

storage = MemoryStorage()
bot = Bot(token=TOKEN, storage=storage)

dp = Dispatcher()

def split_message(text, max_length=4096):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"Hello, {message.from_user.first_name}")
#
# @dp.message(Command("login"))
# async def login(message: types.Message):
#     logging.info()(message.text)
#     if message.text == PASSWORD:
#         await storage.set_data(chat=message.chat.id, data={'id': message.from_user.id})
#     else: await message.answer("Неверный пароль!")
#
# @dp.message(Command("check"))
# async def chech(message: types.Message):
#     data = storage.get_data(message.from_chat.id)
#     if data is None:
#         await message.answer("Ты не в аккаунте")
#     else:
#         await message.answer("Ты в аккаунте")

def sql(query: str):
    try:
        pg = psycopg2.connect(f"""
            host={HOST_PG}
            dbname=postgres
            user={USER_PG}
            password={PASSWORD_PG}
            port={PORT_PG}
        """)

        cursor = pg.cursor(cursor_factory=psycopg2.extras.DictCursor)

        logging.info(query)

        cursor.execute(query[1:])

        rows = cursor.fetchall()

        return_data = []

        for row in rows:
            a = dict(row)
            for i in a.items():
                if type(i[1]) == datetime.datetime:
                    a[i[0]] = str(i[1])
            return_data.append(a)

        pg.commit()

        logging.info('Ответ получен!')

    except (Exception, Error) as error:
        logging.error(f'DB: ', error)

        return_data = f"Error: {Error}"

    finally:
        if pg:
            cursor.close()
            pg.close()
            logging.info("Соединение с PostgreSQL закрыто")
            return return_data

def json_serializable(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Преобразуем datetime в строку
    raise TypeError("Type not serializable")

@dp.message(Command("sql"))
async def cmd_sql(message: types.Message):
    logging.info(message.text)
    logging.info(message.from_user.id)
    logging.info(IDS)
    if str(message.from_user.id) in IDS:
        result = sql(message.text.lstrip("/sql"))
        text = str(result).replace("'",'"')
        logging.info(text)
        result = json.loads(text)
        result = json.dumps(result, indent=4)
        logging.info(result)
        for jsonchik in result:
            for part in split_message(str(jsonchik)):
                logging.info(part)
                logging.info(type(part))
                # razeik = json.loads(part.replace("'",'"'))
                # await message.answer(json.dumps(razeik, indent=4))

    else: await message.answer("Вы не админ")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
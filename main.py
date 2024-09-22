import asyncio
import aiohttp
import uuid
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.storage.memory import MemoryStorage
import psycopg2
from psycopg2 import extras, Error
import logging
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta
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

# storage = MemoryStorage()
bot = Bot(token=TOKEN)  # Ваш токен
dp = Dispatcher(storage=MemoryStorage())

waiting_for_html = False

def split_message(text, max_length=4096):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if str(message.from_user.id) in IDS:
        await message.answer(f"Hello, {message.from_user.first_name}")
    else: await message.answer("Вы не админ")


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

@dp.message(Command("add_news"))
async def cmd_add_news(message: types.Message):
    if str(message.from_user.id) in IDS:
        global waiting_for_html
        waiting_for_html = True
        await message.reply("Отправьте файл HTML.")
    else: await message.answer("Вы не админ")

def add_news(html):
    try:
        pg = psycopg2.connect(f"""
            host={HOST_PG}
            dbname=postgres
            user={USER_PG}
            password={PASSWORD_PG}
            port={PORT_PG}
        """)

        cursor = pg.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute(f"INSERT INTO news({uuid.uuid4().hex}, {html}, {datetime.now() + timedelta(days=7)}, {[]})")

        pg.commit()

        return_data = "Ok"

    except (Exception, Error) as error:
        logging.error(f'DB: ', error)

        return_data = f"Error: {Error}"

    finally:
        if pg:
            cursor.close()
            pg.close()
            logging.info("Соединение с PostgreSQL закрыто")
            return return_data


@dp.message(F.document)
async def handle_document(message: types.Message):
    if str(message.from_user.id) in IDS:
        global waiting_for_html
        if waiting_for_html:
            document = message.document
            if document.mime_type == 'text/html':
                file_info = await bot.get_file(document.file_id)
                file_url = f'https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}'

                async with aiohttp.ClientSession() as session:  # Используем aiohttp для запросов
                    async with session.get(file_url) as response:
                        if response.status == 200:
                            content = await response.read()
                            reiz = add_news(content)
                            logging.info(reiz)
                            await message.reply(reiz)
                        else:
                            await message.reply("Не удалось загрузить файл.")
            else:
                await message.reply("Формат файла неправильный. Пожалуйста, отправьте HTML файл.")
        waiting_for_html = False
    else: await message.answer("Вы не админ")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
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
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
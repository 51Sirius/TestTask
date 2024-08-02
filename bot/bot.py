import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiohttp
import asyncio

API_TOKEN = 'TOKEN'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

API_URL = "http://web:8000/api/v1"


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Привет! Я бот для управления сообщениями. Используй /get_messages для просмотра всех сообщений и /add_message для добавления нового сообщения.")


@dp.message(Command("get_messages"))
async def get_messages(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/messages/") as resp:
            messages = await resp.json()
            if messages:
                await message.answer("\n".join([f"{msg['user']}: {msg['content']}" for msg in messages]))
            else:
                await message.answer("Сообщений пока нет.")


@dp.message(Command("add_message"))
async def add_message(message: types.Message):
    await message.answer("Введите сообщение в формате 'user: content'.")


@dp.message()
async def handle_message(message: types.Message):
    if ":" not in message.text:
        await message.answer("Неверный формат. Используйте 'user: content'.")
        return

    user, content = message.text.split(":", 1)
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/message/", json={"user": user.strip(), "content": content.strip()}) as resp:
            if resp.status == 200:
                await message.answer("Сообщение успешно добавлено!")
            else:
                await message.answer("Ошибка при добавлении сообщения.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

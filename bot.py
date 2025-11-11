import asyncio
import os
import aiohttp
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
import logging

# Загружаем .env переменные
load_dotenv()

# Получаем токены
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

logging.basicConfig(level=logging.INFO)

# Проверяем, что всё загружено
if not BOT_TOKEN or not OPENROUTER_API_KEY:
    raise ValueError("Проверь .env файл! Отсутствует BOT_TOKEN или OPENROUTER_API_KEY.")

# Настройки OpenRouter
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://yourdomain.com",
    "X-Title": "TelegramLLMBot"
}

# Асинхронная функция общения с LLM
async def ask_llm(user_message):
    payload = {
        "model": "openai/gpt-4o",
        "messages": [
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 1000
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(BASE_URL, headers=HEADERS, json=payload) as response:
            data = await response.json()

            if response.status == 200 and "choices" in data:
                return data["choices"][0]["message"]["content"]
            else:
                return f"Ошибка LLM:\nStatus: {response.status}\n{data}"

# Создаём экземпляры бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет! Я AI-бот. Напиши мне сообщение — и я спрошу у LLM")

# /help
@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer("Просто напиши любой текст — и я постараюсь ответить через OpenRouter GPT-4o.")

# Обычные сообщения
@dp.message(F.text)
async def message_handler(message: Message):
    user_input = message.text
    reply = await ask_llm(user_input)
    await message.answer(reply)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())

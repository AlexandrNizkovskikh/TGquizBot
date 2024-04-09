import asyncio
import logging
from aiogram import Bot, Dispatcher
from quiz_database import create_table

from handlers import ruoter


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()

    API_TOKEN = '7057679019:AAGu6O0cKylrSbLdqYhSBgobxJohWT_2CHY'

    # Объект бота
    bot = Bot(token=API_TOKEN)

    # Диспетчер
    dp = Dispatcher()
    dp.include_router(ruoter)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
from aiogram import types, Router, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from quiz_date import quiz_data
from quiz_database import update_quiz_index, get_quiz_index, get_user_score, update_user_score
from keyboard import generate_options_keyboard


ruoter = Router()

# Хэндлер на команду /help
@ruoter.message(Command("help"))
async def cmd_start(message: types.Message):
    await message.answer("Список команд: \n/start - Перезапустить бота\n/help - все команды\n/quiz - начать игру")

# Хэндлер на команду /start
@ruoter.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Моя статистика"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


# Хэндлер на команду /mystat
@ruoter.message(F.text == "Моя статистика")
@ruoter.message(Command("mystat"))
async def cmd_mystat(message: types.message):
    user_id = message.from_user.id
    user_score = await get_user_score(user_id)
    await message.answer(f"Ваша статистика:\nПравильных ответов: {user_score}")

# Хэндлер на команду /quiz
@ruoter.message(F.text=="Начать игру")
@ruoter.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

async def new_quiz(message):
    # получаем id пользователя, отправившего сообщение
    user_id = message.from_user.id
    # сбрасываем значение текущего индекса вопроса квиза в 0
    current_question_index = 0
    new_score = 0
    await update_quiz_index(user_id, current_question_index)
    await update_user_score(user_id, new_score)
    # запрашиваем новый вопрос для квиза
    await get_question(message, user_id)


async def get_question(message, user_id):

    # Запрашиваем из базы текущий индекс для вопроса
    current_question_index = await get_quiz_index(user_id)
    # Получаем индекс правильного ответа для текущего вопроса
    correct_index = quiz_data[current_question_index]['correct_option']
    # Получаем список вариантов ответа для текущего вопроса
    opts = quiz_data[current_question_index]['options']

    # Функция генерации кнопок для текущего вопроса квиза
    # В качестве аргументов передаем варианты ответов и значение правильного ответа (не индекс!)
    kb = generate_options_keyboard(opts, opts[correct_index])
    # Отправляем в чат сообщение с вопросом, прикрепляем сгенерированные кнопки
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


@ruoter.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):

    current_question_index = await get_quiz_index(callback.from_user.id)

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    selected_option = callback.data

    await callback.message.answer(f"Ваш ответ - {selected_option} Верно!")
    
    
    current_score = await get_user_score(callback.from_user.id)

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    current_score += 1

    await update_quiz_index(callback.from_user.id, current_question_index)
    await update_user_score(callback.from_user.id, current_score)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


@ruoter.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    current_score = await get_user_score(callback.from_user.id)

    correct_option = quiz_data[current_question_index]['correct_option']

    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1

    await update_quiz_index(callback.from_user.id, current_question_index)
    await update_user_score(callback.from_user.id, current_score)


    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
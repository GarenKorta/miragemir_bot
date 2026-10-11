import asyncio
import random
import logging
import os
import json

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Для создания профиля
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


# =========================
# НАСТРОЙКИ
# =========================

from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")   

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# =========================
# ДАННЫЕ ПОЛЬЗОВАТЕЛЕЙ
# =========================

user_data = {}

# Активные игры
games = {}


# =========================
# ЗАГРУЗКА ДАННЫХ
# =========================

def load_data():
    global user_data

    if os.path.exists("user.json"):
        with open("user.json", "r", encoding="utf-8") as f:
            user_data = json.load(f)


# =========================
# СОХРАНЕНИЕ ДАННЫХ
# =========================

def save_data():
    with open("user.json", "w", encoding="utf-8") as f:
        json.dump(
            user_data,
            f,
            ensure_ascii=False,
            indent=4
        )


load_data()


# =========================
# СОСТОЯНИЯ ПРОФИЛЯ
# =========================

class Profile(StatesGroup):
    name = State()
    color = State()


# =========================
# REPLY-КНОПКИ
# =========================

reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="😂 Шутка про программиста"),
            KeyboardButton(text="🎨 Шутка про дизайнера")
        ]
    ],
    resize_keyboard=True
)


# =========================
# ШУТКИ
# =========================

programmer_jokes = [
    "💻 Программист — это человек, который решает проблему, о существовании которой ты ещё не знал.",
    "🐛 Программист: «Это не баг, это неожиданная функция!»",
    "☕ Сколько программистов нужно, чтобы поменять лампочку? Ни одного. Это hardware-проблема.",
    "⌨️ Программист может написать код без ошибок. Но только в теории."
]

designer_jokes = [
    "🎨 Дизайнер: «Сделаем просто». Клиент: «А можно добавить ещё 47 элементов?»",
    "🖌️ Дизайнер знает, что идеальный пиксель существует. Клиент — нет.",
    "🎨 Клиент: «Сделайте красиво». Дизайнер: «А что именно красиво?» Клиент: «Ну... красиво!»",
    "🖥️ Дизайнер: «Какой цвет вам нравится?» Клиент: «Синий». Дизайнер: «Какой именно?» Клиент: «Ну, синий!»"
]


# =========================
# КОМАНДА /START
# =========================

@dp.message(Command("start"))
async def start_command(message: Message):

    await message.answer(
        "👋 Привет!\n\n"
        "Доступные команды:\n\n"
        "🚪 /doors — сыграть в игру «Двери»\n"
        "👤 /profile — создать или посмотреть профиль\n"
        "ℹ️ /about — информация о боте\n"
        "🔄 /start — показать это меню\n\n"
        "Также у тебя есть кнопки с рандомными шутками 👇",
        reply_markup=reply_keyboard
    )


# =========================
# КОМАНДА /ABOUT
# =========================

@dp.message(Command("about"))
async def about_command(message: Message):

    await message.answer(
        "🤖 О Боте\n\n"
        "Это бот с игрой «Двери» и профилями пользователей.\n\n"
        "🚪 В игре есть 3 двери.\n"
        "🎯 Только одна дверь правильная.\n"
        "🎲 Правильная дверь выбирается случайно.\n\n"
        "👤 В профиле можно сохранить имя "
        "и любимый цвет."
    )


# =========================
# ПРОФИЛЬ
# =========================

@dp.message(Command("profile"))
async def profile_command(message: Message, state: FSMContext):

    user_id = str(message.from_user.id)

    # Сбрасываем старое состояние
    await state.clear()

    # Проверяем, есть ли профиль
    if user_id in user_data:

        profile = user_data[user_id]

        # Проверяем, заполнены ли имя и цвет
        if "name" in profile and "color" in profile:

            await message.answer(
                "👤 Твой профиль\n\n"
                f"Имя: {profile['name']}\n"
                f"🎨 Любимый цвет: {profile['color']}\n\n"
                "Если хочешь изменить профиль, "
                "напиши /profile ещё раз."
            )

            return

    # Если профиля нет или он неполный
    await message.answer(
        "👤 Давай создадим твой профиль!\n\n"
        "Как тебя зовут?"
    )

    await state.set_state(Profile.name)


# =========================
# ПОЛУЧАЕМ ИМЯ
# =========================

@dp.message(Profile.name)
async def profile_name(message: Message, state: FSMContext):

    if not message.text:
        await message.answer(
            "❗ Пожалуйста, напиши своё имя текстом."
        )
        return

    name = message.text.strip()

    if not name:
        await message.answer(
            "❗ Имя не может быть пустым.\n"
            "Попробуй ещё раз."
        )
        return

    # Сохраняем имя
    await state.update_data(name=name)

    await message.answer(
        "🎨 Отлично!\n\n"
        "Теперь напиши свой любимый цвет."
    )

    await state.set_state(Profile.color)


# =========================
# ПОЛУЧАЕМ ЦВЕТ
# =========================

@dp.message(Profile.color)
async def profile_color(message: Message, state: FSMContext):

    if not message.text:
        await message.answer(
            "❗ Пожалуйста, напиши цвет текстом."
        )
        return

    color = message.text.strip()

    if not color:
        await message.answer(
            "❗ Цвет не может быть пустым.\n"
            "Попробуй ещё раз."
        )
        return

    # Получаем имя
    data = await state.get_data()

    name = data.get("name")

    if not name:
        await state.clear()

        await message.answer(
            "❗ Что-то пошло не так.\n\n"
            "Давай начнём заново.\n"
            "Напиши /profile"
        )
        return

    user_id = str(message.from_user.id)

    # Сохраняем профиль
    user_data[user_id] = {
        "name": name,
        "color": color
    }

    # Сохраняем в JSON
    save_data()

    # Очищаем состояние
    await state.clear()

    await message.answer(
        "✅ Профиль сохранён!\n\n"
        f"👤 Имя: {name}\n"
        f"🎨 Любимый цвет: {color}\n\n"
        "Теперь ты можешь посмотреть профиль "
        "командой /profile."
    )


# =========================
# КОМАНДА /DOORS
# =========================

@dp.message(Command("doors"))
async def doors_command(message: Message):

    user_id = message.from_user.id

    # Выбираем правильную дверь
    correct_door = random.randint(1, 3)

    games[user_id] = correct_door

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="🚪 Дверь 1",
        callback_data="door_1"
    )

    keyboard.button(
        text="🚪 Дверь 2",
        callback_data="door_2"
    )

    keyboard.button(
        text="🚪 Дверь 3",
        callback_data="door_3"
    )

    keyboard.adjust(3)

    await message.answer(
        "🎮 Игра началась!\n\n"
        "Перед тобой три двери.\n"
        "Только одна из них правильная.\n\n"
        "Выбери дверь:",
        reply_markup=keyboard.as_markup()
    )


# =========================
# ПРОДОЛЖЕНИЕ ИГРЫ
# =========================

@dp.callback_query(F.data == "doors")
async def continue_game(callback: CallbackQuery):

    user_id = callback.from_user.id

    correct_door = random.randint(1, 3)

    games[user_id] = correct_door

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="🚪 Дверь 1",
        callback_data="door_1"
    )

    keyboard.button(
        text="🚪 Дверь 2",
        callback_data="door_2"
    )

    keyboard.button(
        text="🚪 Дверь 3",
        callback_data="door_3"
    )

    keyboard.adjust(3)

    await callback.message.edit_text(
        "🎮 Новая игра началась!\n\n"
        "Перед тобой снова три двери.\n"
        "Выбери одну:",
        reply_markup=keyboard.as_markup()
    )

    await callback.answer()


# =========================
# ВЫБОР ДВЕРИ
# =========================

@dp.callback_query(lambda callback: callback.data.startswith("door_"))
async def choose_door(callback: CallbackQuery):

    user_id = callback.from_user.id

    if user_id not in games:

        await callback.answer(
            "Эта игра уже закончилась. Запусти новую через /doors.",
            show_alert=True
        )

        return

    selected_door = int(
        callback.data.split("_")[1]
    )

    correct_door = games[user_id]

    if selected_door == correct_door:

        result = (
            "🎉 ПОБЕДА!\n\n"
            f"Ты выбрал дверь №{selected_door}.\n"
            f"Правильная дверь — №{correct_door} ✅"
        )

    else:

        result = (
            "❌ Ты проиграл!\n\n"
            f"Ты выбрал дверь №{selected_door}.\n"
            f"Правильная дверь — №{correct_door} 🚪"
        )

    del games[user_id]

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="🚪 Продолжить игру",
        callback_data="doors"
    )

    keyboard.button(
        text="ℹ️ О Боте",
        callback_data="about"
    )

    keyboard.adjust(1)

    await callback.message.edit_text(
        result,
        reply_markup=keyboard.as_markup()
    )

    await callback.answer()


# =========================
# INLINE-КНОПКА «О БОТЕ»
# =========================

@dp.callback_query(F.data == "about")
async def about_bot(callback: CallbackQuery):

    await callback.answer()

    await callback.message.answer(
        "🤖 О Боте\n\n"
        "Это бот с небольшой игрой «Двери».\n\n"
        "🚪 Всего есть 3 двери.\n"
        "🎯 Только одна дверь правильная.\n"
        "🎲 Правильная дверь выбирается случайно.\n\n"
        "👤 Также можно создать профиль "
        "с помощью команды /profile."
    )


# =========================
# ШУТКА ПРО ПРОГРАММИСТА
# =========================

@dp.message(F.text == "😂 Шутка про программиста")
async def programmer_joke(message: Message):

    joke = random.choice(programmer_jokes)

    await message.answer(joke)


# =========================
# ШУТКА ПРО ДИЗАЙНЕРА
# =========================

@dp.message(F.text == "🎨 Шутка про дизайнера")
async def designer_joke(message: Message):

    joke = random.choice(designer_jokes)

    await message.answer(joke)


# =========================
# ЗАПУСК БОТА
# =========================

async def main():

    logging.basicConfig(level=logging.INFO)

    print("🤖 Бот запущен!")

    await dp.start_polling(bot)


# =========================
# ЗАПУСК ПРОГРАММЫ
# =========================

if __name__ == "__main__":
    asyncio.run(main())
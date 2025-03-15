import aiogram.exceptions
from aiogram import types, F, Router, Bot
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from rasberry.data import test_generation
from tools.database import *
from datetime import datetime

from tools.notification import Notification
from tools.tools import is_admin

dp = Router()


@dp.callback_query(F.data == "start")
async def start(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Настройки",
        callback_data="settings")
    )
    if is_admin(callback.from_user.id):
        builder.add(types.InlineKeyboardButton(
            text="Админ панель",
            callback_data="admin_panel")
        )
        builder.add(types.InlineKeyboardButton(
            text="Панель управления",
            callback_data="panel")
        )
    builder.adjust(1, 1, 1)
    await callback.answer()
    await callback.message.edit_text(f'''Приветствуем вас в боте для управления автономным агрокомплексом''',
                                     reply_markup=builder.as_markup())


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    conn = create_connection()
    add_user(conn, {'user_id': message.from_user.id, 'username': message.from_user.username})
    conn.close()
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Настройки",
        callback_data="settings")
    )
    if is_admin(message.from_user.id):
        builder.add(types.InlineKeyboardButton(
            text="Админ панель",
            callback_data="admin_panel")
        )
        builder.add(types.InlineKeyboardButton(
            text="Панель управления",
            callback_data="panel")
        )
    builder.adjust(1, 1, 1)
    await message.answer(f'''Приветствуем вас в боте для управления автономным агрокомплексом''',
                         reply_markup=builder.as_markup())


@dp.callback_query(F.data == "panel")
async def panel(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Получить график по сенсорам за период",
        callback_data="panel.graph.period")
    )
    builder.add(types.InlineKeyboardButton(
        text="Получить график по сенсорам за день",
        callback_data="panel.graph.today")
    )
    builder.add(types.InlineKeyboardButton(
        text="Назад",
        callback_data="start")
    )
    builder.adjust(1, 1, 1)
    await callback.answer()
    try:
        await callback.message.edit_text(f'''<b>Панель управления агрономным комплексом</b>''',
                                         reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except aiogram.exceptions.TelegramBadRequest as e:
        await callback.message.delete()
        await callback.message.answer(f'''<b>Панель управления агрономным комплексом</b>''',
                                      reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


@dp.callback_query(F.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Тестовая генерация значений датчика",
        callback_data="test.gen")
    )
    builder.add(types.InlineKeyboardButton(
        text="Назад",
        callback_data="start")
    )
    builder.adjust(1, 1)

    await callback.answer()
    await callback.message.edit_text("""<b>Панель администратора</b>
    
Для отправки уведомления, используйте команду /send_notification""", reply_markup=builder.as_markup(),
                                     parse_mode=ParseMode.HTML)


@dp.callback_query(F.data == "test.gen")
async def test_gen(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Тестовая генерация значений датчика",
        callback_data="test.gen")
    )
    builder.add(types.InlineKeyboardButton(
        text="Назад",
        callback_data="admin_panel")
    )
    builder.adjust(1, 1)
    await test_generation()
    await callback.answer()
    await callback.message.edit_text("""<b>Панель администратора</b>

Данные успешно сгенерированы""", reply_markup=builder.as_markup(),
                                     parse_mode=ParseMode.HTML)


@dp.callback_query(F.data == "settings")
async def settings(callback: types.CallbackQuery):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE user_id = {callback.from_user.id};")
    user = cursor.fetchone()
    conn.close()
    contains_one = lambda t=user: 1 == t[3]
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Настройка уведомлений",
        callback_data="settings.notifications"
    ))
    builder.add(types.InlineKeyboardButton(
        text="Назад",
        callback_data="start")
    )
    builder.adjust(1, 1)
    await callback.answer()
    try:
        await callback.message.edit_text(text=f"""<b>Пользователь</b> {callback.from_user.mention_html()}
<b>ID</b>: {callback.from_user.id}
<b>Права администратора</b>: {contains_one()}
<b>Аккаунт зарегистрирован</b>: {user[4]}""", reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except aiogram.exceptions.TelegramBadRequest:
        pass


"""
@dp.callback_query(F.data == "id")
async def id_get(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Назад",
        callback_data="settings")
    )
    await callback.message.edit_text(text = f"Твой ID: {callback.from_user.id}", reply_markup=builder.as_markup())
    await callback.answer()
"""

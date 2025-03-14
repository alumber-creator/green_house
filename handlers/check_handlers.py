

from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tools.database import create_connection
from tools.notification import Notification

dp = Router()


async def get_checks_state(user_id: int):
    """Получаем текущие состояния чекбоксов для пользователя"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_checks WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()

    if not user_data:
        # Создаем новую запись с дефолтными значениями
        cursor.execute("INSERT INTO user_checks (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        return (0, 0, 0)  # Возвращаем значения по умолчанию
    conn.close()
    return user_data[1:]  # Пропускаем user_id


def generate_keyboard(checks_state):
    """Генерируем inline-клавиатуру на основе состояний"""
    check_usernames = ['Уведомления о критических ситуациях', 'Уведомления о выполнении операций', 'Уведомления с рекомендациями']
    check_names = ['check1', 'check2', 'check3']
    keyboard = InlineKeyboardBuilder()

    for check_username, check_name, state in zip(check_usernames, check_names, checks_state):
        status = "✅" if state else "❌"
        button = types.InlineKeyboardButton(
            text=f"{check_username} {status}",
            callback_data=f"toggle_check:{check_name}"
        )
        keyboard.add(button)
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="settings"))
    keyboard.adjust(1,1,1,1)
    return keyboard

@dp.callback_query(lambda c: c.data.startswith('settings.notifications'))
async def show_checks(callback: types.CallbackQuery):
    """Обработчик команды для показа чекбоксов"""
    checks_state = await get_checks_state(callback.from_user.id)
    keyboard = generate_keyboard(checks_state)
    await callback.answer()
    await callback.message.edit_text("""<b>Настройка уведомлений:</b>
    
Выберите опции""", reply_markup=keyboard.as_markup(), parse_mode=ParseMode.HTML)



@dp.callback_query(lambda c: c.data.startswith('toggle_check'))
async def toggle_check(callback_query: types.CallbackQuery):
    """Обработчик переключения чекбокса"""
    conn = create_connection()
    cursor = conn.cursor()
    user_id = callback_query.from_user.id
    check_name = callback_query.data.split(':')[1]

    # Обновляем состояние в базе данных
    cursor.execute(f'''UPDATE user_checks 
                   SET {check_name} = NOT {check_name}
                   WHERE user_id = ?''',
                   (user_id,))
    conn.commit()

    # Получаем обновленные состояния
    checks_state = await get_checks_state(user_id)
    keyboard = generate_keyboard(checks_state)
    conn.close()
    await callback_query.answer()
    await callback_query.message.edit_reply_markup(reply_markup=keyboard.as_markup())

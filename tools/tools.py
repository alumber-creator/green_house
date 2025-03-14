import calendar
from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder

from tools.database import create_connection


def is_admin(id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f'''SELECT is_admin FROM users WHERE user_id = {id}''')
    user = cursor.fetchone()
    if user[0]:
        return True
    return False


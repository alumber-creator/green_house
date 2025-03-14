from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State

from tools.database import create_connection
from aiogram import Bot

from tools.tools import is_admin


class Notification:
    def __init__(self, text: str, notification_class: int, bot: Bot):
        self.text = text
        self.notification_class = notification_class
        self.bot = bot

    async def send_notification(self):
        conn = create_connection()
        cursor = conn.cursor()
        if self.notification_class != 4:
            cursor.execute(f'''SELECT * FROM user_checks WHERE check{self.notification_class} == 1''')
        else:
            cursor.execute(f'''SELECT * FROM user_checks''')
        users = cursor.fetchall()
        conn.close()
        for user in users:
            await self.bot.send_message(chat_id=user[0], text=self.text, parse_mode=ParseMode.HTML)


class NotificationStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_level = State()





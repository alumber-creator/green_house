# Генерация inline-календаря
from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder

import calendar


def generate_calendar_keyboard(view_type='days', year=None, month=None, mode='default'):
    today = datetime.today()
    year = year or today.year
    month = month or today.month
    builder = InlineKeyboardBuilder()


    if view_type == 'days':
        if mode == 'daily':
            builder.button(text=f"Сегодня {datetime.now().strftime("%d.%m.%Y")}", callback_data=f"day_{today.year}_{today.month}_{today.day}")
        # Заголовок с кнопкой выбора месяца/года
        month_year = f"{datetime(year, month, 1).strftime('%B %Y')}"
        builder.button(text=month_year, callback_data="nav_month_year")


        # Дни недели
        for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
            builder.button(text=day, callback_data="ignore")

        # Дни месяца
        month_days = calendar.monthcalendar(year, month)
        for week in month_days:
            for day in week:
                if day == 0:
                    builder.button(text=" ", callback_data="ignore")
                else:
                    builder.button(
                        text=str(day),
                        callback_data=f"day_{year}_{month}_{day}"
                    )

        # Кнопки навигации
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1

        builder.button(text="←", callback_data=f"nav_month_{prev_year}_{prev_month}")
        builder.button(text="→", callback_data=f"nav_month_{next_year}_{next_month}")
        if mode == 'daily':
            builder.adjust(1, 1, *[7] * 2)
        else:
            builder.adjust(1, *[7] * 2)
    elif view_type == 'months':
        builder.button(text=f"Выберите месяц в {year} году:", callback_data="ignore")
        for i, month_name in enumerate(calendar.month_name[1:], start=1):
            builder.button(
                text=month_name,
                callback_data=f"select_month_{year}_{i}"
            )
        builder.button(text=f"← Год {year - 1}", callback_data=f"nav_year_{year - 1}")
        builder.button(text=f"Год {year + 1} →", callback_data=f"nav_year_{year + 1}")
        builder.adjust(1, *[3] * 4, 2)

    elif view_type == 'years':
        builder.button(text="Выберите год:", callback_data="ignore")
        for y in range(year - 5, year + 6):
            builder.button(
                text=str(y),
                callback_data=f"select_year_{y}"
            )
        builder.adjust(1, *[5] * 2)

    return builder.as_markup()
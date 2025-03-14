import calendar
import io
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from aiogram import F, Router, Bot, types
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta

from matplotlib.dates import DateFormatter

from tools.calendars import generate_calendar_keyboard
from tools.database import SENSORS
from tools.sensors import SensorStates

dp = Router()

def maxs(a: int, max: int):
    if(a>max): return max
    else: return a

@dp.callback_query(F.data == "panel.graph.today")
async def cmd_daily(callback: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    for sensor in SENSORS:
        keyboard.button(text=sensor.capitalize(), callback_data=f"daily_sensor_{sensor}")
    keyboard.adjust(1)
    await callback.answer()
    await callback.message.edit_text("Выберите датчик для дневного графика:", reply_markup=keyboard.as_markup())
    await state.set_state(SensorStates.choosing_day)

# Обработчик выбора датчика для daily
@dp.callback_query(F.data.startswith("daily_sensor_"), SensorStates.choosing_day)
async def daily_sensor_selected(callback: CallbackQuery, state: FSMContext):
    sensor = callback.data.split("_")[2]
    await state.update_data(sensor=sensor)
    await callback.answer()
    await callback.message.edit_text(
        "Выберите день:",
        reply_markup=generate_calendar_keyboard(mode='daily')
    )
    await state.set_state(SensorStates.choosing_day)



@dp.callback_query(F.data.startswith('day_'), SensorStates.choosing_day)
async def handle_daily_date(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if callback.data == "daily_today":
        selected_date = datetime.today()
    else:
        _, year, month, day = callback.data.split('_')
        selected_date = datetime(int(year), int(month), int(day))

    # Устанавливаем временные рамки дня
    start_date = selected_date.replace(hour=0, minute=0, second=0)
    end_date = selected_date.replace(hour=23, minute=59, second=59)

    data = await state.get_data()
    sensor_name = data['sensor']

    # Получаем данные из БД
    conn = sqlite3.connect('sensors.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"SELECT value, time FROM {sensor_name} "
            "WHERE time BETWEEN ? AND ? ORDER BY time",
            (start_date.timestamp(), end_date.timestamp())
        )
        results = cursor.fetchall()
    finally:
        conn.close()

    if not results:
        await callback.answer()
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Назад",
            callback_data="panel")
        )
        await callback.message.edit_text("Данные за выбранный день отсутствуют", reply_markup=builder.as_markup())
        await state.clear()
        return

    # Генерация графика с более детальным отображением
    dates = [datetime.fromtimestamp(row[1]) for row in results]
    values = [row[0] for row in results]

    plt.figure(figsize=(12, 6))
    plt.plot(dates, values, marker='o', linestyle='-', color='green')
    avg_value = np.mean(values)
    plt.axhline(y=avg_value, color='r', linestyle='--',
                label=f'Среднее: {avg_value:.2f}')
    plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    plt.title(f"{sensor_name.capitalize()} за {selected_date.strftime('%d.%m.%Y')}")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.grid(True)
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(maxs(len(dates), 15)))
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Сохранение в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close()

    # Отправка графика
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Назад",
        callback_data="panel")
    )
    await callback.answer()
    await callback.message.delete()
    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=BufferedInputFile(buf.read(), filename='daily_graph.png'),
        caption=f"Данные за {selected_date.strftime('%d.%m.%Y')}",
        reply_markup = builder.as_markup()
    )
    await state.clear()


'''ЗА ПЕРИОД'''

@dp.callback_query(F.data.startswith("nav_"))
async def handle_navigation(callback: CallbackQuery, state: FSMContext):
    action, *params = callback.data.split('_')

    if action == "nav":
        if params[0] == "month":
            year, month = map(int, params[1:3])
            await callback.message.edit_reply_markup(
                reply_markup=generate_calendar_keyboard('days', year, month)
            )
        elif params[0] == "year":
            year = int(params[1])
            await callback.message.edit_reply_markup(
                reply_markup=generate_calendar_keyboard('months', year)
            )
        elif params[0] == "month":
            await callback.message.edit_reply_markup(
                reply_markup=generate_calendar_keyboard('months', int(params[1]))
            )
        elif params[0] == "year":
            await callback.message.edit_reply_markup(
                reply_markup=generate_calendar_keyboard('years', int(params[1]))
            )


@dp.callback_query(F.data.startswith("select_"))
async def handle_selection(callback: CallbackQuery, state: FSMContext):
    action, *params = callback.data.split('_')

    if action == "select":
        if params[0] == "year":
            year = int(params[1])
            await callback.message.edit_reply_markup(
                reply_markup=generate_calendar_keyboard('months', year)
            )
            await state.set_state(SensorStates.choosing_month)
        elif params[0] == "month":
            year, month = map(int, params[1:3])
            await callback.message.edit_reply_markup(
                reply_markup=generate_calendar_keyboard('days', year, month)
            )
            await state.set_state(SensorStates.choosing_start_date)

@dp.callback_query(F.data == "nav_month_year")
async def handle_month_year_nav(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()

    if current_state in [SensorStates.choosing_start_date, SensorStates.choosing_end_date]:
        await callback.answer()
        await callback.message.edit_reply_markup(
            reply_markup=generate_calendar_keyboard('years')
        )
        await state.set_state(SensorStates.choosing_year)


# Команда старта
@dp.callback_query(F.data == "panel.graph.period")
async def cmd_graph(callback: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    for sensor in SENSORS:
        keyboard.button(text=sensor.capitalize(), callback_data=f"sensor_{sensor}")
    keyboard.adjust(1)
    await callback.answer()
    await callback.message.edit_text("Выберите датчик:", reply_markup=keyboard.as_markup())
    await state.set_state(SensorStates.choosing_sensor)

# Обработчик выбора датчика
@dp.callback_query(F.data.startswith("sensor_"), SensorStates.choosing_sensor)
async def sensor_selected(callback: CallbackQuery, state: FSMContext):
    sensor = callback.data.split("_")[1]
    await state.update_data(sensor=sensor)
    await callback.message.edit_text(
        "Выберите начальную дату:",
        reply_markup=generate_calendar_keyboard('years')
    )
    await callback.answer()
    await state.set_state(SensorStates.choosing_year)


# Обработчик выбора даты
@dp.callback_query(F.data.startswith('day_'),
                   StateFilter(SensorStates.choosing_start_date, SensorStates.choosing_end_date))
async def date_selected(callback: CallbackQuery, state: FSMContext, bot: Bot):
    _, year, month, day = callback.data.split('_')
    selected_date = datetime(int(year), int(month), int(day))

    current_state = await state.get_state()
    data = await state.get_data()

    if current_state == SensorStates.choosing_start_date.state:
        await state.update_data(start_date=selected_date)
        await callback.answer()
        await callback.message.edit_text("Выберите конечную дату:",
                                         reply_markup=generate_calendar_keyboard())
        await state.set_state(SensorStates.choosing_end_date)
    else:
        await state.update_data(end_date=selected_date)
        message = await callback.message.edit_text("Собираю данные...")

        # Получение данных из БД
        sensor_data = data['sensor']
        start = data['start_date'].timestamp()
        end = selected_date.timestamp()

        conn = sqlite3.connect('sensors.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT value, time FROM {sensor_data} WHERE time BETWEEN ? AND ?",
                       (start, end))
        results = cursor.fetchall()
        conn.close()

        if not results:
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(
                text="Назад",
                callback_data="panel")
            )
            await callback.message.answer("Нет данных за выбранный период", reply_markup=builder.as_markup(),
                                          parse_mode=ParseMode.HTML)
            await state.clear()
            return

        # Построение графика
        times = [datetime.fromtimestamp(row[1]) for row in results]
        times.sort()
        values = [row[0] for row in results]
        if (selected_date - data['start_date']).days > 3:
            plt.figure(figsize=(20, 7))
        else:
            plt.figure(figsize=(20, 12))
        plt.rcParams['axes.linewidth'] = 1.5
        plt.rcParams['axes.edgecolor'] = 'gray'
        plt.rcParams['axes.xmargin'] = 0.1
        plt.plot(times, values)
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(maxs(len(times), 50)))
        if (selected_date - data['start_date']).days < 3:
            plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.xticks(rotation=45)
        plt.title(f"{sensor_data.capitalize()} over time {times[0]} - {times[len(times)-1]}")
        plt.xlabel("Time")
        plt.ylabel("Value")
        avg_value = np.mean(values)
        plt.axhline(y=avg_value, color='r', linestyle='--',
                    label=f'Среднее: {avg_value:.2f}')
        plt.grid(True)
        plt.legend()
        plt.savefig('chart.png', format='png')
        plt.close()

        # Отправка графика
        with open('chart.png', 'rb') as chart_file:
            input_file = BufferedInputFile(chart_file.read(), filename='chart.png')
            await callback.answer()
            await message.delete()
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(
                text="Назад",
                callback_data="panel")
            )
            await bot.send_photo(callback.from_user.id, photo=input_file, caption="График за выбранное время:", reply_markup=builder.as_markup())

        await state.clear()


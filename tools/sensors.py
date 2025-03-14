from aiogram.fsm.state import StatesGroup, State


class SensorStates(StatesGroup):
    choosing_sensor = State()
    choosing_start_date = State()
    choosing_end_date = State()
    choosing_year = State()
    choosing_month = State()
    choosing_day = State()

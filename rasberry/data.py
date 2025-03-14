import datetime
import random

from numpy import real

from tools.database import *


def insert_sensors(sensor: str, value: float, time: datetime.datetime):
    conn = create_connection(name='../sensors.db')
    cursor = conn.cursor()
    cursor.execute(f'''INSERT INTO {sensor} (value, time) VALUES ({value}, {time})''')
    conn.commit()
    conn.close()


def generate_random_datetimes(start_str, end_str, count=1):
    try:
        start_date = start_str
        end_date = end_str
    except ValueError as e:
        raise ValueError("Неверный формат даты. Используйте ГГГГ-ММ-ДД ЧЧ:ММ:СС") from e

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    start_ts = start_date.timestamp()
    end_ts = end_date.timestamp()

    results = []
    for _ in range(count):
        random_ts = random.uniform(start_ts, end_ts)
        random_date = datetime.datetime.fromtimestamp(random_ts)
        results.append(random_date)

    return results



if __name__ == "__main__":
    init_db('../sensors.db')
    start_date = datetime.datetime(2025, 3, 1)
    end_date = datetime.datetime(2025, 3, 31)
    for i in generate_random_datetimes(start_date, end_date, 1000):
        value = random.randint(10, 100)
        time = i
        print(time)
        insert_sensors("light", value, time.timestamp())


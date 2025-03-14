import sqlite3
from sqlite3 import Error
from time import sleep

# Список доступных датчиков
SENSORS = ["temperature", "humidity", "light"]


def create_connection(recon: int = 15, times: int = 3, name="telegram_bot.db"):
    """Создает соединение с базой данных SQLite"""
    if times <= 0: return None
    conn = None
    try:
        # Создаем или подключаемся к файлу базы данных
        conn = sqlite3.connect(name)
        print("Подключение к SQLite успешно!")
        print(name)
        return conn
    except Error as e:
        print(f"Ошибка подключения: {e}")
        if recon > 0:
            for i in range(recon):
                print(f"Повторная попытка подключения через {i}")
                sleep(1)
            return create_connection(recon, times - 1, name)


# Инициализация базы данных сенсоров
def init_db(name='sensors.db'):
    SENSORS = ["temperature", "humidity", "light"]
    conn = sqlite3.connect(name)
    cursor = conn.cursor()
    for sensor in SENSORS:
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {sensor}
                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        value FLOAT,
                        time DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()


def create_table(conn):
    """Создает таблицу users, если она не существует"""
    try:
        cursor = conn.cursor()
        # SQL-запрос для создания таблицы
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL UNIQUE,
            username TEXT,
            is_admin BOOLEAN,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """
        cursor.execute(create_table_query)
        conn.commit()  # Фиксируем изменения
        print("Таблица 'users' создана или уже существует")
        # Создаем таблицу с отдельными колонками для каждого чекбокса
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_checks (
                         user_id INTEGER PRIMARY KEY,
                         check1 INTEGER DEFAULT 0,
                         check2 INTEGER DEFAULT 0,
                         check3 INTEGER DEFAULT 0)''')
        conn.commit()
        print("Таблица 'user_notification' создана или уже существует")
        init_db()  # База данных сенсоров
    except Error as e:
        print(f"Ошибка при создании таблицы: {e}")


def add_user(conn, user_data):
    """Добавляет нового пользователя в таблицу"""
    cursor = conn.cursor()
    try:
        # Вставка данных через параметры (защита от SQL-инъекций)
        cursor.execute('''
            INSERT INTO users (user_id, username) 
            VALUES (?, ?)
        ''', (user_data['user_id'], user_data['username']))
        conn.commit()
        print(f"Пользователь {user_data['user_id']} добавлен")
    except sqlite3.IntegrityError:
        print("Пользователь уже существует!")


def get_all_users(conn):
    """Возвращает всех пользователей из таблицы"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    return rows


def update_username(conn, user_id, new_username):
    """Обновляет имя пользователя"""
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET username = ? 
        WHERE user_id = ?
    ''', (new_username, user_id))
    conn.commit()
    print(f"Имя пользователя {user_id} обновлено")


def delete_user(conn, user_id):
    """Удаляет пользователя по ID"""
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    conn.commit()
    print(f"Пользователь {user_id} удален")


"""
# Пример использования
if __name__ == "__main__":
    # 1. Создаем соединение и таблицу
    conn = create_connection()
    if conn:
        create_table(conn)

        # 2. Добавляем тестовых пользователей
        add_user(conn, {
            'user_id': 12345,
            'username': 'ivan_petrov',
            'first_name': 'Иван'
        })

        add_user(conn, {
            'user_id': 67890,
            'username': None,  # Допустимо, если поле не обязательное
            'first_name': 'Мария'
        })

        # 3. Получаем всех пользователей
        print("\nВсе пользователи:")
        users = get_all_users(conn)
        for user in users:
            print(user)

        # 4. Обновляем username
        update_username(conn, 12345, 'ivan_updated')

        # 5. Удаляем пользователя
        delete_user(conn, 67890)

        # 6. Проверяем результат
        print("\nПосле изменений:")
        for user in get_all_users(conn):
            print(user)

        # Закрываем соединение
        conn.close()
"""

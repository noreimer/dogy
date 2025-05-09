import os
import sqlite3
from app import app

def init_db():
    # Убедитесь, что папка instance существует
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # Путь к базе данных
    db_path = os.path.join(app.instance_path, 'breed.db')

    # Подключение к базе данных (или создание, если её нет)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Проверка существования файла breed.sql
    sql_file_path = os.path.join(app.instance_path, 'breed.sql')
    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(f"SQL file not found at {sql_file_path}")

    # Чтение SQL-скрипта и выполнение
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    cursor.executescript(sql_script)

    # Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")

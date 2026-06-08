import sqlite3

# 1. Підключаємося до "битої" бази в режимі читання
try:
    old_conn = sqlite3.connect('../python_academy/db.sqlite3', uri=True)
    new_conn = sqlite3.connect('db.sqlite3')

    # 2. Переносимо дані уроків (якщо вони ще доступні)
    old_cur = old_conn.cursor()
    new_cur = new_conn.cursor()

    # Спробуємо витягнути дані
    data = old_cur.execute("SELECT id, title, intro_text, author_text, history_text FROM courses_lesson").fetchall()

    for row in data:
        new_cur.execute(
            "INSERT OR IGNORE INTO courses_lesson (id, title, intro_text, author_text, history_text) VALUES (?, ?, ?, ?, ?)",
            row)

    new_conn.commit()
    print("Дані перенесено!")

except sqlite3.DatabaseError as e:
    print(f"Помилка бази даних (вона занадто пошкоджена): {e}")
finally:
    old_conn.close()
    new_conn.close()
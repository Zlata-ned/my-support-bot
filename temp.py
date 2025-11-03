import sqlite3

# 1. ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ
connection = sqlite3.connect('mydb.sqlite')
cursor = connection.cursor()

print("=== Пример 1: Получить всех студентов ===")
cursor.execute("SELECT * FROM students")
result = cursor.fetchall()
print("Тип результата:", type(result))
print("Результат:", result)
print()

# 2. РЕЗУЛЬТАТ - ЭТО СПИСОК КОРТЕЖЕЙ
print("=== Пример 2: Обработка каждой строки ===")
cursor.execute("SELECT name, age FROM students")
for row in cursor.fetchall():
    print(f"Имя: {row[0]}, Возраст: {row[1]}")
print()

# 3. FETCHONE - получить одну строку
print("=== Пример 3: Получить только первого студента ===")
cursor.execute("SELECT * FROM students")
first_student = cursor.fetchone()
print("Первый студент:", first_student)
print()

# 4. ПАРАМЕТРИЗОВАННЫЕ ЗАПРОСЫ (безопасно!)
print("=== Пример 4: Поиск по городу ===")
city_to_find = 'Москва'
cursor.execute("SELECT name FROM students WHERE city = ?", (city_to_find,))
moscow_students = cursor.fetchall()
print(f"Студенты из {city_to_find}:")
for student in moscow_students:
    print(f"  - {student[0]}")
print()

# 5. ПОДСЧЁТ КОЛИЧЕСТВА
print("=== Пример 5: Сколько студентов на 1 курсе? ===")
cursor.execute("SELECT COUNT(*) FROM students WHERE course = 1")
count = cursor.fetchone()[0]
print(f"Студентов на 1 курсе: {count}")
print()

# 6. ДОБАВЛЕНИЕ ДАННЫХ ИЗ PYTHON
print("=== Пример 6: Добавление нового студента ===")
new_student = ('Елена', 20, 2, 'Казань')
cursor.execute(
    "INSERT INTO students (name, age, course, city) VALUES (?, ?, ?, ?)",
    new_student
)
connection.commit()  # ВАЖНО! Сохраняем изменения
print("Студент добавлен!")
print()

# 7. СЛОВАРИ ВМЕСТО КОРТЕЖЕЙ (удобнее!)
print("=== Пример 7: Результат как словари ===")
cursor.execute("SELECT * FROM students")
for row in cursor.fetchall():
    print({'id': row[0], 'name': row[1], 'age': row[2], 'course': row[3], 'city': row[4]})

# Закрываем соединение
connection.close()
from flask import Flask, render_template, request  # Импортируем необходимые модули
from datetime import datetime
import json
import os

app = Flask(__name__)  # Создаем экземпляр приложения, исправлено name на __name__

# Функция для загрузки сообщений из файла
def load_messages():
    if not os.path.exists("db.json") or not os.path.getsize("db.json") > 0:  # Исправлено на "db.json"
        return []
    with open("db.json", "r") as file:  # Исправлено на "db.json"
        data = json.load(file)
    return data.get("messages", [])

all_messages = load_messages()

# Функция для добавления сообщения
def add_message(author, text):
    message = {
        "author": author,
        "text": text,
        "time": datetime.now().strftime("%H:%M:%S")
    }
    all_messages.append(message)  # Добавляем сообщение в список всех сообщений
    save_message()

# Функция для сохранения сообщений в файл
def save_message():
    all_messages_data = {
        "messages": all_messages
    }
    with open("db.json", "w") as file:  # Исправлено на "db.json"
        json.dump(all_messages_data, file)

@app.route("/")  # Эндпоинт начальной страницы
def main_page():
    return "ты вообще читал README.md ? напиши /chat к ссылке и проходи"

@app.route("/chat")
def chat_page():
    return render_template("form.html")

@app.route("/get_messages")
def get_messages():
    print("Отдаем все сообщения")
    return {"messages": all_messages}

@app.route("/send_message")
def send_message():
    name = request.args.get("name")  # Получаем данные из query параметров запроса к серверу
    text = request.args.get("text")
    print(f"пользователь '{name}' пишет '{text}'")
    add_message(name, text)
    return "ok"

if __name__ == '__main__':  # Исправлено на __name__ == '__main__'
    app.run(host='0.0.0.0', port=8080)  # Конфигурируем параметры запуска приложения

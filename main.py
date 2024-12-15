from flask import Flask, render_template, request
from datetime import datetime
import json
import os

app = Flask(__name__)

# Хранение всех сообщений
all_messages = []

# Словарь для отслеживания количества отправленных сообщений пользователями
user_message_count = {}
MESSAGE_LIMIT = 10  # Ограничение на количество сообщений


def load_messages():
    if not os.path.exists("db.json") or not os.path.getsize("db.json") > 0:
        return []
    with open("db.json", "r") as file:
        data = json.load(file)
    return data.get("messages", [])


def add_message(author, text):
    message = {
        "author": author,
        "text": text,
        "time": datetime.now().strftime("%H:%M:%S")
    }
    all_messages.append(message)
    save_message()


def save_message():
    all_messages_data = {
        "messages": all_messages
    }
    with open("db.json", "w") as file:
        json.dump(all_messages_data, file)


@app.route("/")
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
    name = request.args.get("name")
    text = request.args.get("text")
    print(f"пользователь '{name}' пишет '{text}'")

    # Проверка количества отправленных сообщений
    if name not in user_message_count:
        user_message_count.clear() # если другой пользователь написал сообщение, то все лимиты обнуляются
        user_message_count[name] = 0
    # Увеличиваем счетчик сообщений пользователя
    user_message_count[name] += 1

    if user_message_count[name] > MESSAGE_LIMIT:
        return "Превышен лимит на отправку сообщений. Пожалуйста, подождите.", 429
    add_message(name, text)

    return "ok"


if __name__ == '__main__':
    app.run(host='26.98.190.163', port=8080)

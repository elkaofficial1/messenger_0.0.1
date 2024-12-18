from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import json
import os
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Установите свой секретный ключ

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


def load_users():
    if not os.path.exists("users.json") or not os.path.getsize("users.json") > 0:
        return {}
    with open("users.json", "r") as file:
        return json.load(file)


def save_users(users):
    with open("users.json", "w") as file:
        json.dump(users, file)


@app.route("/")
def main_page():
    return "подробности в README"


@app.route("/chat")
def chat_page():
    return render_template("form.html")


@app.route("/get_messages")
def get_messages():
    print("Отдаем все сообщения")
    return {"messages": all_messages}


@app.route("/send_message")
def send_message():
    name = session.get("username")  # Используем имя пользователя из сессии
    text = request.args.get("text")
    print(f"пользователь '{name}' пишет '{text}'")

    # Проверка количества отправленных сообщений
    if name not in user_message_count:
        user_message_count.clear()  # если другой пользователь написал сообщение, то все лимиты обнуляются
        user_message_count[name] = 0

    user_message_count[name] += 1

    if user_message_count[name] > MESSAGE_LIMIT:
        return "Превышен лимит на отправку сообщений. Пожалуйста, подождите.", 429

    add_message(name, text)
    return "ok"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Хеширование пароля
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        users = load_users()

        if username in users:
            return "Пользователь с этим именем уже существует.", 400  # Ошибка пользователя

        # Сохранение пользователя
        users[username] = password_hash
        save_users(users)
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        users = load_users()

        if username in users and users[username] == password_hash:
            session["username"] = username
            return redirect(url_for("chat_page"))
        return "Неверное имя пользователя или пароль.", 401

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("main_page"))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

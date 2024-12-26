from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import json
import os
import bcrypt
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
MESSAGE_LIMIT = 10

USERS_FILE = "users.json"
CHATS_FILE = "chats.json"
MESSAGES_FILE = "db.json"


def load_users():
    if not os.path.exists(USERS_FILE) or not os.path.getsize(USERS_FILE) > 0:
        return {}
    with open(USERS_FILE, "r") as file:
        return json.load(file)


def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)


def load_chats():
    if not os.path.exists(CHATS_FILE) or not os.path.getsize(CHATS_FILE) > 0:
        return []
    with open(CHATS_FILE, "r") as file:
        return json.load(file)


def save_chats(chats):
    with open(CHATS_FILE, "w") as file:
        json.dump(chats, file)


def load_messages(chat_id):
    if not os.path.exists(MESSAGES_FILE) or not os.path.getsize(MESSAGES_FILE) > 0:
        return []
    with open(MESSAGES_FILE, "r") as file:
        data = json.load(file)
    return data.get(str(chat_id), [])


def save_message(chat_id, message):
    all_messages = load_messages(chat_id)
    all_messages.append(message)

    # Загружаем существующие данные или инициализируем пустой словарь
    if not os.path.exists(MESSAGES_FILE) or os.path.getsize(MESSAGES_FILE) == 0:
        data = {}
    else:
        with open(MESSAGES_FILE, "r") as file:
            data = json.load(file)

    data[str(chat_id)] = all_messages

    # Сохраняем обратно в файл
    with open(MESSAGES_FILE, "w") as file:
        json.dump(data, file)


@app.route("/")
def main_page():
    return "подробности в README"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        users = load_users()

        if username in users:
            return "Пользователь с этим именем уже существует.", 400

        users[username] = password_hash.decode()
        save_users(users)
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()

        if username in users and bcrypt.checkpw(password.encode(), users[username].encode()):
            session["username"] = username
            return redirect(url_for("chat_page"))
        return "Неверное имя пользователя или пароль.", 401

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("main_page"))


@app.route("/chat")
def chat_page():
    if "username" not in session:
        return redirect(url_for("login"))

    chats = load_chats()
    return render_template("chat_list.html", chats=chats)


@app.route("/create_chat", methods=["GET", "POST"])
def create_chat():
    if request.method == "POST":
        if "username" not in session:
            return redirect(url_for("login"))

        chat_name = request.form["chat_name"]
        participants = request.form.getlist("participants")

        chat_id = str(uuid.uuid4())
        chat = {
            "chat_id": chat_id,
            "name": chat_name,
            "participants": participants,
            "messages": []
        }

        chats = load_chats()
        chats.append(chat)
        save_chats(chats)

        return redirect(url_for("chat_page"))

    users = load_users()
    return render_template("create_chat.html", users=users)


@app.route("/chat/<chat_id>")
def view_chat(chat_id):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    chats = load_chats()
    chat = next((c for c in chats if c["chat_id"] == chat_id), None)

    if not chat:
        return "Чат не найден", 404

    if username not in chat["participants"]:
        return "У вас нет доступа к этому чату", 403

    messages = load_messages(chat_id)
    return render_template("chat.html", chat=chat, messages=messages)


@app.route("/send_message/<chat_id>", methods=["POST"])
def send_message(chat_id):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    text = request.form["text"]

    chats = load_chats()
    chat = next((c for c in chats if c["chat_id"] == chat_id), None)

    if not chat:
        return "Чат не найден", 404

    if username not in chat["participants"]:
        return "У вас нет доступа к этому чату", 403

    # Ограничение на количество сообщений
    user_messages = [msg for msg in load_messages(chat_id) if msg["author"] == username]
    if len(user_messages) >= MESSAGE_LIMIT:
        return f"Вы достигли лимита в {MESSAGE_LIMIT} сообщений в этом чате.", 403

    message = {
        "author": username,
        "text": text,
        "time": datetime.now().strftime("%H:%M:%S")
    }

    save_message(chat_id, message)
    return redirect(url_for("view_chat", chat_id=chat_id))


@app.route("/load_messages/<chat_id>")
def load_messages_route(chat_id):
    messages = load_messages(chat_id)
    return jsonify(messages)


if __name__ == "__main__":
    app.run(host='26.98.190.163', port=8080)

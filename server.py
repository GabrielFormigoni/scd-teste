from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from threading import Lock
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = "seu_secret_key_aqui"
socketio = SocketIO(app)
thread = None
thread_lock = Lock()
text = ""
text_timestamp = 0
cursor_positions = {}


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def handle_connect():
    emit("connected", {"data": "Conectado com sucesso!"})
    emit(
        "text_update", {"text": text}
    )  # Envia o texto atual para o cliente recém-conectado
    emit(
        "all_cursor_positions", cursor_positions
    )  # Envia as posições de cursor atuais para o cliente recém-conectado


@socketio.on("text_update")
def handle_text_update(data):
    global text
    received_text = data["text"]
    received_timestamp = data["timestamp"]

    if received_timestamp > text_timestamp:
        with thread_lock:
            text = received_text
            text_timestamp = received_timestamp

    emit("text_update", {"text": text, "timestamp": text_timestamp}, broadcast=True)


@socketio.on("get_text")
def handle_get_text():
    global text, text_timestamp
    emit("text_update", {"text": text, "timestamp": text_timestamp})


@socketio.on("cursor_position")
def handle_cursor_position(data):
    global cursor_positions
    cursor_positions[request.sid] = data
    emit("all_cursor_positions", cursor_positions, broadcast=True)


@socketio.on("disconnect")
def handle_disconnect():
    global cursor_positions
    if request.sid in cursor_positions:
        del cursor_positions[request.sid]
        emit("all_cursor_positions", cursor_positions, broadcast=True)


if __name__ == "__main__":
    port = 5000
    socketio.run(app, host="0.0.0.0", port=port)

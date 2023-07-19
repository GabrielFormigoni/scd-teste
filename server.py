from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from threading import Lock

app = Flask(__name__)
app.config["SECRET_KEY"] = "seu_secret_key_aqui"
socketio = SocketIO(app)
thread = None
thread_lock = Lock()
text = ""
cursor_positions = {}


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def handle_connect():
    emit("connected", {"data": "Conectado com sucesso!"})


@socketio.on("text_update")
def handle_text_update(data):
    global text
    with thread_lock:
        text = data["text"]
    emit("text_update", data, broadcast=True)


@socketio.on("get_text")
def handle_get_text():
    global text
    emit("text_update", {"text": text})


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
    socketio.run(app)

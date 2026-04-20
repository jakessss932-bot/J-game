from flask import Flask, request
from flask_socketio import SocketIO, emit
import uuid
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",   # Python 3.14 compatible
    transports=["websocket", "polling"]
)

players = {}
sid_to_pid = {}

@app.route("/")
def home():
    return "Multiplayer server is running!"

@socketio.on("connect")
def on_connect():
    pid = str(uuid.uuid4())
    sid_to_pid[request.sid] = pid
    players[pid] = {"x": 100, "y": 100}

    emit("init", {"id": pid, "players": players})
    emit("player_joined", {"id": pid, "pos": players[pid]}, broadcast=True, include_self=False)

@socketio.on("move")
def on_move(data):
    pid = data["id"]
    players[pid] = data["pos"]
    emit("move", data, broadcast=True, include_self=False)

@socketio.on("disconnect")
def on_disconnect():
    sid = request.sid
    if sid in sid_to_pid:
        pid = sid_to_pid[sid]

        if pid in players:
            del players[pid]

        emit("player_left", {"id": pid}, broadcast=True)
        del sid_to_pid[sid]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port)

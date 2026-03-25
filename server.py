from flask import Flask
from flask_socketio import SocketIO, emit
import uuid

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

players = {}

@app.route("/")
def home():
    return "Multiplayer server is running!"

@socketio.on("connect")
def on_connect():
    player_id = str(uuid.uuid4())
    players[player_id] = {"x": 100, "y": 100}

    emit("init", {"id": player_id, "players": players})
    emit("player_joined", {"id": player_id, "pos": players[player_id]}, broadcast=True)

@socketio.on("move")
def on_move(data):
    pid = data["id"]
    players[pid] = data["pos"]
    emit("move", data, broadcast=True)

@socketio.on("disconnect")
def on_disconnect():
    for pid in list(players.keys()):
        emit("player_left", {"id": pid}, broadcast=True)
        del players[pid]
        break

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)

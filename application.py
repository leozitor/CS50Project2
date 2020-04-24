import os

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)
# list of channels
channels = ["General"]

# list of users {"username": {"username":"Leozitor", "channel":"canal"}}
users = {}

users_sid = {}


#room message message limit
roomMessageLimit = 100

private_messages = {}  # keys are the private rooms
messages = {
    "General": ["mensagem 1", "mensagem 2", "mensagem 3", "mensagem 4", "mensagem 5", "mensagem 6", "mensagem 7"]
}


def printAll():
    print("Users List:")
    print(users)
    print("--------------------------")
    print("Users_sid List:")
    print(users_sid)
    print("--------------------------")
    print("Channels List:")
    print(channels)
    print("--------------------------")
    print("Message Rooms dict")
    print(messages)
    print()


@app.route("/")
def index():
    return render_template("index.html", channels=channels, messages=messages)


@socketio.on("add user")
def addUser(data):
    username = data
    # If not find user, adds to users dict
    if username not in users:
        users[username] = {"username": username, "channel": "General"}
        users_sid[request.sid] = username
        print("User {} Connected".format(users[username]))
        print("user sid {}".format(users_sid[request.sid]))
        printAll()
    else:
        users_sid[request.sid] = username
        print("User {} Connected".format(users[username]))
        print("user sid {}".format(request.sid))
        printAll()

    emit("welcome user", {"usersList": list(users), "channelsList": channels}, broadcast=True)


@socketio.on("send message")
def sendMessage(data):
    msg = data["message"]
    channel = data["channel"]
    if len(messages[channel]) >= roomMessageLimit:
        messages[channel].append(msg)
        messages[channel].pop(0)
    else:
        messages[channel].append(msg)
    printAll()
    emit("announce messages", messages[channel], room=channel)



@socketio.on("user connected")
def userConnected(channel):
    # check if channel really exists if user was connected with the browser opened after server restart
    if channel not in channels:
        emit("reset channel", broadcast=False)
    else:
        id = request.sid
        users[users_sid[id]]["channel"] = channel
        print("User sid {}".format(id))
        print("User {} connected sending messages".format(users_sid[id]))
        join_room(channel)
        #print("Data = {}".format(data))
        #print("Mensagens: {}".format(messages[data]))
        printAll()
        emit("announce messages", messages[channel], broadcast=False)


@socketio.on("create channel")
def createChannel(data):
    if data in channels:
        emit("channelError")
    else:
        channels.append(data)  # appending to channels list
        messages[data] = []  # creating new message room to the dictionarie
        printAll()
        emit("announce channel creation", data, broadcast=True)


@socketio.on("change channel")
def changeChannel(channel):
    id = request.sid
    users[users_sid[id]]["channel"] = channel
    join_room(channel)
    printAll()
    emit("announce messages", messages[channel], broadcast=False)


@socketio.on("disconnect")
def user_disconnect():
    # SID from user disconnected
    id = request.sid
    username = users_sid.pop(id)
    if username not in users_sid.values():
        users.pop(username)
        print("User {} Disconnected".format(username))
        print("User sid {}".format(id))
        emit("user removed", list(users), broadcast=True)
    else:
        print("User {} still exists".format(username))
        print("Only last connection {} was removed from sid list ".format(id))
    printAll()

@socketio.on("test")
def test(data):
    print("Deu CERTO----------------------------------------------------------------------")

if __name__ == '__main__':
    socketio.run(app)




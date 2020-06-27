from flask import Flask, request, jsonify
import json
import os
import uuid
import datetime as dt


app = Flask(__name__, static_url_path='')
app.secret_key = 'thisisasecretkey'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


# USER MANAGEMENT ROUTES
@app.route("/api/login", methods=["GET"])
def login():
    username = request.json["email"]
    password = request.json["password"]
    json_file = open("./login.json", "r+")
    users = json.load(json_file)
    pswd = users.get(username)
    if(pswd == password):
        data = {
            "status": "ok"
        }
        return jsonify(data)
    else:
        data = {
            "status": "not ok"
        }
        return jsonify(data)


@app.route("/api/register", methods=["POST"])
def register():
    user = {}
    username = request.json['email']
    password = request.json['password']
    user.update({
        username: password
    })
    try:
        json_file = open("./login.json", "r+")
        data = json.load(json_file)
        for key, value in data.items():
            if(username == key):
                data = {
                    "status": "user exists"
                }
                return jsonify(data)
        data.update(user)
        json_file.seek(0)
        json.dump(data, json_file)
        json_file.close()
        data = {
            "status": "ok"
        }
        return jsonify(data)
    except:
        data = {
            "status": "not ok"
        }
        return jsonify(data)

# DATA MANAGEMENT ROUTES
# Route for Creating a TODO ("POST" route) and Getting all TODOs ("GET" route) #


@app.route("/api/todo", methods=["POST", "GET"])
def todos():
    if request.method == "POST":
        # data = []
        todo = {}
        tid = str(uuid.uuid4())
        email = request.json['email']
        topic = request.json['topic']
        todoString = request.json['todoString']
        status = "not done"
        curDate = dt.datetime.now()
        day = curDate.strftime("%d-%m-%Y")
        time = curDate.strftime("%H:%M")
        timestamp = day + ", at " + time
        todo.update(
            {
                "id": tid,
                "email": email,
                "topic": topic,
                "todoString": todoString,
                "status": status,
                "timestamp": timestamp
            }
        )
        json_file = open("./todos.json", "r+")
        data = json.load(json_file)
        json_file.close()
        data.append(todo)
        json_file = open("./todos.json", "w")
        json_file.seek(0)
        json.dump(data, json_file)
        json_file.close()
        resp = {
            "status": "ok"
        }
        return jsonify(resp)
    else:
        todos = []
        email = request.json['email']
        json_file = open("./todos.json", "r+")
        data = list(json.load(json_file))
        json_file.close()
        data.reverse()
        for todo in data:
            if(todo["email"] == email):
                todos.append(todo)
        return jsonify(todos)

# Route for changing "status" of a particular TODO #


@app.route("/api/todo/<tid>/changestatus", methods=["GET"])
def changestatus(tid):
    todos = []
    json_file = open("./todos.json", "r+")
    data = json.load(json_file)
    json_file.close()
    for todo in data:
        if(todo['id'] == tid):
            if(todo["status"] == "done"):
                todo["status"] = "not done"
            else:
                todo["status"] = "done"
        todos.append(todo)
    json_file = open("./todos.json", "w")
    json_file.seek(0)
    json.dump(todos, json_file)
    json_file.close()
    return jsonify(todos)


# Route to search TODO #
@app.route("/api/todo/search")
def search():
    todos = []
    text = request.json["text"]
    if(text == ""):
        json_file = open("./todos.json", "r+")
        data = list(json.load(json_file))
        data.reverse()
        return jsonify(data)
    else:
        json_file = open("./todos.json", "r+")
        data = json.load(json_file)
        json_file.close()
        for todo in data:
            if ((text.lower() in todo["topic"].lower()) or (text.lower() in todo["todoString"].lower())):
                todos.append(todo)
        todos.reverse()
        return jsonify(todos)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)

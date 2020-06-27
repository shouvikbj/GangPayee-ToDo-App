from flask import Flask, render_template, redirect, request, url_for, session, flash, jsonify, make_response
import json
import os
import uuid
import requests


app = Flask(__name__, static_url_path='')
app.secret_key = 'thisisasecretkey'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# USER MANAGEMENT ROUTES


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("email")
        password = request.form.get("password")
        data = {
            "email": username,
            "password": password
        }
        response = requests.get(
            "https://todoserver.pythonanywhere.com/api/login", json=data)
        details = response.json()
        if(details["status"] == "ok"):
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('email', username, max_age=60*60*24*365*2)
            flash("Logged in !", "primary")
            return resp
        else:
            flash("Invalid Credentials !", "primary")
            return redirect(url_for('login'))
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("email")
        password = request.form.get("password")
        data = {
            "email": username,
            "password": password
        }
        response = requests.post(
            "https://todoserver.pythonanywhere.com/api/register", json=data)
        res = response.json()
        if(res['status'] == 'ok'):
            flash("Account Created !", "primary")
            return redirect(url_for('login'))
        elif(res["status"] == "user exists"):
            flash("Email already in use !", "danger")
            return redirect(url_for('signup'))
        else:
            flash("Account Not Created !", "warning")
            return redirect(url_for('signup'))
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('email', expires=0)
    flash("Logged out", "primary")
    return resp

# DATA MANAGEMENT ROUTES
# Route to Home Page #


@app.route("/", methods=["POST", "GET"])
def index():
    if request.cookies.get('email'):
        if request.method == "GET":
            email = request.cookies.get('email')
            data = {
                "email": email
            }
            response = requests.get(
                "https://todoserver.pythonanywhere.com/api/todo", json=data)
            todos = response.json()
            return render_template("index.html", todos=todos)
        else:
            email = str(request.cookies.get('email'))
            topic = request.form.get("topic")
            todoString = request.form.get("todoString")
            data = {
                "email": email,
                "topic": topic,
                "todoString": todoString
            }
            response = requests.post(
                "https://todoserver.pythonanywhere.com/api/todo", json=data)
            resp = response.json()
            if(resp['status'] == "ok"):
                msg = "ToDo '{}' added.".format(topic)
                flash(msg, "primary")
                return redirect(url_for('index'))
            else:
                flash("ToDo could not be added", "warning")
                return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

# Route to change TODO staus #


@app.route("/todo/<tid>/changestatus", methods=["GET"])
def changestatus(tid):
    url = "https://todoserver.pythonanywhere.com/api/todo/{}/changestatus".format(
        tid)
    response = requests.get(url)
    return redirect(url_for('index'))

# Route to search TODO #


@app.route("/todo/search", methods=["POST", "GET"])
def search():
    result = []
    email = request.cookies.get('email')
    text = request.form.get("text")
    data = {
        "text": text
    }
    response = requests.get(
        "https://todoserver.pythonanywhere.com/api/todo/search", json=data)
    data = response.json()
    for todo in data:
        if(todo["email"] == email):
            result.append(todo)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=True)

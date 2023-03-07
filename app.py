from flask import Flask, session, render_template, redirect, url_for, request
from dotenv import load_dotenv
import os
from database import create_new_user_in_db, login_against_db, create_new_thread_on_db, find_threads_for_user,retrieve_entire_thread,get_id_from_username

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ['FLASK_SECRET_KEY']

@app.route("/")
def index():
    if 'username' in session:
        return render_template('profile_homepage.html', session=session,
        threads=find_threads_for_user(str(session["user_id"])))
    return redirect(url_for('show_login_form'))

@app.get("/login")
def show_login_form():
    return render_template("login.html")

@app.post("/login")
def do_the_login():
    data = request.form
    username = data["username"]
    password = data["password"]
    result = login_against_db(username,password)
    if result:
        session.permanent = False
        session["username"] = result[0]
        session["email"] = result[1]
        session["user_id"] = result[2]
        return redirect(url_for('index'))
    return "<p>login failed</p>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.get("/create-account")
def show_account_creation():
    return render_template("create-account.html")

@app.post("/create-account")
def create_new_account():
    data = request.form
    username = data["username"]
    password = data["password"]
    email = data["email"]
    result = create_new_user_in_db(username,password,email)
    if result:
        return f"""<p>Created successfully {username}!</p>
         <a href="/">Return home</a>"""
    else:
        return "<p>Account creation unsuccessful</p>"


@app.get("/create-thread")
def create_new_thread():
    if 'username' in session:
        return render_template('create-thread.html', session=session)
    return redirect(url_for('show_login_form'))

@app.post("/create-thread")
def save_new_thread():
    data = request.form
    next_user_id = get_id_from_username(data['next-user'])
    if next_user_id:
        thread_id = create_new_thread_on_db(data['user-id'],data["message-text"],next_user_id)
        return redirect(url_for("view_thread",thread_id=thread_id))
    return "<p>That user doesn't exist</p>"

@app.route("/view-thread/<thread_id>")
def view_thread(thread_id):
    if 'username' in session:
        thread = retrieve_entire_thread(thread_id)
        thread_users = [user[1] for user in thread]
        if session['username'] in thread_users:
            return render_template("view-thread.html", thread_id=thread_id, thread=thread[:-1],next_user=thread_users[-1],
            username=session['username'])
    return redirect(url_for('index')) 
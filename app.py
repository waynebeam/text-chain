from flask import Flask, session, render_template, redirect, url_for, request
from dotenv import load_dotenv
import os
from database import create_new_user_in_db, login_against_db, create_new_thread_on_db, find_threads_for_user,retrieve_entire_thread,get_id_from_username, update_user_thread_status, add_message_to_thread

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ['FLASK_SECRET_KEY']

@app.route("/")
def index():
    if 'username' in session:
        text_id_viewed_length = find_threads_for_user(str(session["user_id"]))
        return render_template('profile_homepage.html', session=session,
        threads=text_id_viewed_length)
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
        update_user_thread_status(data['user-id'], thread_id,1)
        update_user_thread_status(next_user_id,thread_id,0)
        return redirect(url_for("view_thread",thread_id=thread_id))
    return "<p>That user doesn't exist</p>"

@app.route("/view-thread/<thread_id>")
def view_thread(thread_id):
    if 'username' in session:
        thread = retrieve_entire_thread(thread_id)
        thread_users = [result[1] for result in thread]
        next_user_id = thread[-1][2]
        if session['username'] in thread_users or session['user_id'] == next_user_id:
            update_user_thread_status(get_id_from_username(session['username']),thread_id,len(thread))
            return render_template("view-thread.html", thread_id=thread_id, thread=thread,next_user_id=next_user_id,
            username=session['username'])
    return redirect(url_for('index')) 

@app.post("/add-message")
def add_message():
    data = request.form
    user_id = get_id_from_username(data['username'])
    next_user_id = get_id_from_username(data['next-user'])
    if next_user_id:
        thread_id = data['thread-id']
        text = data['text']
        thread_length = data['thread-length']
        add_message_to_thread(text,thread_id,user_id,next_user_id)   
        update_user_thread_status(next_user_id,thread_id,thread_length)
        return redirect(url_for('index'))
    return "<p>That user doesn't exist</p>"
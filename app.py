from flask import Flask, session, render_template, redirect, url_for
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ['FLASK_SECRET_KEY']

@app.route("/")
def test_homepage():
    if 'username' in session:
        return "<h1>hello User!</p>"
    return redirect(url_for('show_login_form'))

@app.get("/login")
def show_login_form():
    return render_template("login.html")

@app.post("/login")
def do_the_login():
    return "<p>Got the login info! Processing.</p>"

@app.get("/create-account")
def show_account_creation():
    return render_template("create-account.html")

@app.post("/create-account")
def create_new_account():
    return "<p>New account created!</p>"
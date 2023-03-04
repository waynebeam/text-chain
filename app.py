from flask import Flask

app = Flask(__name__)

@app.route("/")
def test_homepage():
    return "<h1>hello world!</p>"
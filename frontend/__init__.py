# Windows: .\.venv\Scripts\python.exe -m flask --app frontend.frontend run
# Open: http://127.0.0.1:5000

from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

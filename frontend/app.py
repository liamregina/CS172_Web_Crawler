# Windows: .\.venv\Scripts\python.exe -m flask --app frontend run --debug
# Macbook: ./.venv/bin/python -m flask --app frontend run --debug

# Open: http://127.0.0.1:5000/

from flask import Flask, request, render_template, url_for, redirect

app = Flask(__name__)

@app.route("/", methods=['GET'])
def search():
    return render_template("search_page.html")

@app.route("/results", methods=['POST'])
def results():
    query_search = request.form.get('query')

    # Pylucune part

    return render_template("results.html")


if __name__ == "__main__":
    app.run(debug=True)
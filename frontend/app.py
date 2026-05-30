# Windows: .\.venv\Scripts\python.exe -m flask --app frontend run --debug
# Macbook: ./.venv/bin/python -m flask --app frontend run --debug

# Open: http://127.0.0.1:5000/

from flask import Flask, request, render_template, url_for, redirect

app = Flask(__name__, static_folder='frontend/static', static_url_path='/static')

@app.route("/", methods=['GET'])
def search():
    return render_template("search_page.html")

@app.route("/results", methods=['POST'])
def results():
    query_search = request.form.get('query')

    # Pylucune part

    # User click search, you should show a list of results (e.g., first 10) returned by Lucene.
    # List should be ordered in decreasing order of score.
    # Give weight to your different fields for ranking.
    # Do not use SOLR or another framework that automatically builds the
    # UI for you

    return render_template("results.html")


if __name__ == "__main__":
    app.run(debug=True)
# Windows: .\.venv\Scripts\python.exe -m flask --app frontend run --debug
# Macbook: ./.venv/bin/python -m flask --app frontend run --debug

# In WSL ubuntu : python -m flask --app frontend.app:app run --debug

# Open: http://127.0.0.1:5000/

from flask import Flask, request, render_template, url_for, redirect
import lucene
from Indexer.searcher import search as lucene_search

app = Flask(__name__, static_folder='frontend/static', static_url_path='/static')

lucene.initVM(vmargs=['-Djava.awt.headless=true'])

@app.route("/", methods=['GET'])
def search():
    return render_template("search_page.html")

@app.route("/results", methods=['POST'])
def results():
    lucene.getVMEnv().attachCurrentThread()
    query_search = request.form.get('query')

    # Pylucene part

    # User click search, you should show a list of results (e.g., first 10) returned by Lucene.
    # List should be ordered in decreasing order of score.
    # Give weight to your different fields for ranking.
    # Do not use SOLR or another framework that automatically builds the
    # UI for you

    indexer_query_output = lucene_search(query_search)
    return render_template("results.html", output=indexer_query_output, query=query_search)


if __name__ == "__main__":
    app.run(debug=True)
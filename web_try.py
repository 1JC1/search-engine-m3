from flask import Flask, request, render_template, redirect, url_for
from time import time

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def ask_for_input():
    error = None
    if request.method == 'POST':
        query = request.form['search']
        return redirect(url_for('results_page', query=query))
    else:
        error = 'Try again'
        
    return render_template('form.html', error=error)

@app.route("/results/<query>", methods=['POST', 'GET'])
def results_page(query: str):
    if request.method == 'POST':
        query = request.form['search']
        return redirect(url_for('results_page', query=query))
    else:
        starttime = time()
        # put search engine running here and return urls (currently using sample urls)
        urls = ["https://www.google.com", "https://flask.palletsprojects.com/en/2.2.x/quickstart/"]
        endtime = time() - starttime
        tagged_urls = [f"<li><a href=\"{u}\">{u}</a></li>" for u in urls]
        url_list = "<ol>" + ''.join(tagged_urls) + "</ol>"
        
        return f"<form method='POST'><input type=\"text\" name=\"search\" placeholder=\"{query}\"> \
        <button type=\"submit\" name=\"submit_button\" >Search</button> <lb> \
        </form> <br><small>({endtime} seconds)</small> {url_list}"
from flask import Flask, request, render_template, redirect, url_for
from search import search, init_url_anchor
from indexer import indexer, create_index, create_index_of_index, open_files, close_files, load_json
from collections import defaultdict
from timeit import default_timer as timer

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
        try:       
            createIndex = False #in case we do not want to create index from scratch
            
            if createIndex:
                create_index()
                url_index, anchor_dict = indexer()
            else:
                open_files() #if we dont create index from scratch, we still want to open all of the files 
                url_index, anchor_dict = load_json()
    
            create_index_of_index()
    
            init_url_anchor(url_index, anchor_dict)
    
            search_start = timer()
            search_results = search(query.strip())
            search_end = timer()
    
        finally:
            close_files()

    tagged_urls = [f"<li><a href=\"{u}\">{u}</a></li>" for u in search_results]
    url_list = "<ol>" + ''.join(tagged_urls) + "</ol>"
    
    return f"<form method='POST'><input type=\"text\" name=\"search\" placeholder=\"{query}\"> \
    <button type=\"submit\" name=\"submit_button\" >Search</button> <lb> \
    </form> <br><small>({search_end - search_start} seconds)</small> {url_list}"
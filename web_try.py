from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def ask_for_input():
    error = None
    if request.method == 'POST':
        query = request.form['search']
        return process_text(query) #replace with actual processing
    else:
        error = 'Try again'
        
    return render_template('form.html', error=error)

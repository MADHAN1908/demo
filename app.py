from flask import Flask,g,render_template,send_file,request, redirect, url_for,session

from db import *
app = Flask(__name__, template_folder='templates')
    
@app.route('/')
def home():
    create_table()
    add_module_count_trigger()
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)

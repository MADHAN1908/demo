from flask import Flask,g,render_template,send_file,request, redirect, url_for,session

from db import *
app = Flask(__name__)
    
@app.route('/')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)

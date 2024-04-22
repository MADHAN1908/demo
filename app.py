from flask import Flask, render_template
from db import get_db 

app = Flask(__name__)

@app.route('/')
def home():
    db = get_db()
    data=[]
    return render_template('home.html', data=data)  

if __name__ == "__main__":
    app.run(debug=True)

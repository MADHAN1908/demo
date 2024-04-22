from flask import Flask
from db import *
app = Flask(__name__)

@app.route('/')
def home():
    create_table()
    add_module_count_trigger()
    return "Welcome"

if __name__ == "__main__":
    app.run(debug=True)

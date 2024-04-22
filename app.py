from flask import Flask,g,render_template,send_file,request, redirect, url_for,session
import subprocess
import base64,os
from io import BytesIO
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from db import *
app = Flask(__name__)
    
@app.route('/')
def home():
    create_table()
    add_module_count_trigger()
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)

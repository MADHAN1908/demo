from flask import Flask,g,render_template,send_file,request, redirect, url_for,session
import subprocess
import base64,os
from io import BytesIO
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import sqlite3
from db import *
app = Flask(__name__)

DATABASE = 'StudySync.db'  
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def getlog(l_id):
    db= get_db()
    cur = db.cursor()
    cur.execute('select * from user_log where log_id = ? ',(l_id,))
    log=cur.fetchone()
    print(log)
    # cur.close()
    return log

def get_next_module_no(course_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT MAX(module_no) FROM course_module WHERE course_id = ?;
    ''', (course_id,))
    max_module_no = cursor.fetchone()[0]
    return (max_module_no + 1) if max_module_no is not None else 1

def get_next_question_no(course_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT MAX(question_no) FROM quiz WHERE course_id = ?;', (course_id,))
    max_question_no = cursor.fetchone()[0]
    return (max_question_no + 1) if max_question_no is not None else 1

def get_next_module_question_no(course_id,module_no):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT MAX(question_no) FROM module_quiz WHERE course_id = ? and module_no= ?;', (course_id,module_no))
    max_question_no = cursor.fetchone()[0]
    return (max_question_no + 1) if max_question_no is not None else 1
  
@app.route('/')
def home():
    create_table()
    add_module_count_trigger()
    return "Welcome"

if __name__ == "__main__":
    app.run(debug=True)

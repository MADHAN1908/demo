from flask import Flask, render_template,request,url_for,redirect
from datetime import datetime
import base64,os
from db import get_db 

app = Flask(__name__)

@app.route('/')
def home():
    confirm=request.args.get('confirm')
    return render_template('home.html',confirm=confirm)
@app.route('/user_message' ,methods=['POST'])
def user_message():
    name=request.form['name']
    email=request.form['email']
    message=request.form['message']
    r_mail="Admin"
    subject="Mail from Home Page"
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db= get_db()
    cur = db.cursor()
    cur.execute('select student_id from student where email_id = ? and student_name = ?',(email,name))
    student=cur.fetchone()
    cur.execute('select * from instructor where email_id = ? and instructor_name = ?',(email,name))
    instructor=cur.fetchone()
    if student or instructor:
        cur.execute('insert into message (sender_email,receiver_email,subject,body,date_time) values(?,?,?,?,?)',(email,r_mail,subject,message,dt))
        db.commit()
        confirm="Message Send Successfully"
        # cur.close()
    else:
         confirm="Invalid UserName or Email ID , Please use the registered UserName and Email ID . "   
    return redirect(url_for('home', _anchor='contact',confirm=confirm))
@app.route('/studentlogin')
def  studentlogin():
    return render_template('studentlogin.html')

@app.route('/adminlogin')
def  admin():
    return render_template('adminlogin.html')

@app.route('/studentdashboard',methods=['POST'])
def  studentdashboard():
    email=request.form.get('email')
    password=request.form.get('password')
    db= get_db()
    cur = db.cursor()
    cur.execute('select student_id,student_name from student where email_id = ? and password = ?',(email,password))
    student=cur.fetchone()
    date =datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if student :
        cur.execute('INSERT INTO student_log (student_id,student_name,login_date) VALUES (?,?,?)', (student[0],student[1],date))
        db.commit()
        cur.execute('select * from student_log where student_id = ? order by login_date DESC ',(student[0],))
        log_id=cur.fetchone()[0]
        print(log_id)
        # session['log_id']=log_id
        # session['student_id']=student[0]
        # session['user_type']="student"
        return redirect(url_for('sd_profile',l_id=log_id,s_id=student[0]))
    else :
         cur.execute('select * from instructor where email_id = ? and password = ?',(email,password))
         instructor=cur.fetchone()
         if instructor :
            if instructor[4]=="Deactivated":
                error = 'Access is Deactivated.'
                return render_template('studentlogin.html', error=error)
            else :
                u_id=instructor[0]
                u_type="Instructor"
                u_name=instructor[1]
                cur.execute('INSERT INTO user_log (user_type,user_id,user_name,login_date) VALUES (?,?,?,?)', (u_type,u_id,u_name,date))
                db.commit()
                cur.execute('select * from user_log where user_id = ? order by login_date DESC ',(instructor[0],))
                log_id=cur.fetchone()[0]
                # cur.close()
                return redirect(url_for('sd_profile',l_id=log_id,u_id=u_id,u_type=u_type,u_name=u_name))
         
         else :
            # cur.close()
            error = 'Invalid username or password. Please try again.'
            return render_template('studentlogin.html', error=error)




@app.route('/logout')
def  logout():
    l_id=request.args.get('l_id')
    s_id=request.args.get('s_id')
    print(l_id,s_id)
    db= get_db()
    cur = db.cursor()
    date =datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if  s_id :
        cur.execute('UPDATE student_log SET logout_date= ? where log_id = ? ',(date,l_id))
        db.commit()
            
    else :
        cur.execute('UPDATE student_log SET logout_date= ? where log_id = ? ',(date,l_id))
        db.commit()
    # cur.close()    
    return redirect('/studentlogin')



@app.route('/studentregister',methods=['POST'])
def  studentregister():
    name=request.form.get('name')
    email=request.form.get('email')
    password=request.form.get('password')
    date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db= get_db()
    cur = db.cursor()
    cur.execute('select student_id,student_name from student where email_id = ?',(email,))
    student=cur.fetchone()
    # cur.close()
    if student :
        error=" Already you have an account account for this Email id"
        return render_template('studentlogin.html',error=error)
    else :
        cur.execute('INSERT INTO student (student_name, email_id, password,sign_up_date) VALUES (?,?,?,?)', (name, email, password,date))
        db.commit()
        # cur.close()
        
        message = "Registration successful. You can now log in."
        return render_template('studentlogin.html', success=message)   
@app.route('/instructor_register',methods=['POST'])
def  instructor_register():
    name=request.form.get('name')
    email=request.form.get('email')
    password=request.form.get('password')
    db= get_db()
    cur = db.cursor()
    cur.execute('select student_id,student_name from student where email_id = ?',(email,))
    student=cur.fetchone()
    cur.execute('select * from instructor where email_id = ?',(email,))
    instructor=cur.fetchone()
    # cur.close()
    if student or instructor :
        error=" Already you have an account account for this Email id"
        return render_template('studentlogin.html',error=error)
    else :
        status="Deactivated"
        cur.execute('INSERT INTO instructor (instructor_name, email_id, password,status) VALUES (?,?,?,?)', (name, email, password,status))
        db.commit()
        # cur.close()
        
        message = "Registration successful. You can now log in."
        return render_template('studentlogin.html', success=message)
@app.route('/sd_profile')
def  sd_profile():
    l_id = request.args.get('l_id')
    s_id = request.args.get('s_id')
    sub="profile"
    return render_template('studentdashboard.html',sub=sub,l_id=l_id,s_id=s_id)
@app.route('/profile')
def  profile():
    s_id = request.args.get('s_id')
    db= get_db()
    cur = db.cursor()
    cur.execute('select * from student where student_id = ?',(s_id,))
    student=cur.fetchone()
    m_no=0
    cur.execute('select course_id,course_name,logo from course WHERE course_id IN (SELECT course_id FROM enroll_course WHERE student_id = ? AND module_no = ? )',(s_id,m_no))
    courses=cur.fetchall()
    courses_with_encoded_images = []
    for course in courses:
        course_list = list(course)  # Convert tuple to list
        image_data = course_list[2]
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        course_list[2] = encoded_image  # Modify the list
        courses_with_encoded_images.append(tuple(course_list))
    cur.execute('select c.course_id,c.course_name,c.logo,a.assessment_id,a.student_name,a.course_name,DATE(a.datetime) from course c JOIN assessment a ON c.course_id = a.course_id WHERE a.student_id = ?',(s_id,))
    completed_courses=cur.fetchall()
    completed_courses_with_encoded_images = []
    for course in completed_courses:
        course_list = list(course)  # Convert tuple to list
        image_data = course_list[2]
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        course_list[2] = encoded_image  # Modify the list
        completed_courses_with_encoded_images.append(tuple(course_list))
    # cur.close()
    return render_template('profile.html',courses=courses_with_encoded_images,completed_courses=completed_courses_with_encoded_images,s_id=student[0], student_name=student[1], email=student[2])

@app.route('/sd_course')
def  sd_course():
    l_id = request.args.get('l_id')
    s_id = request.args.get('s_id')
    sub="course"
    return render_template('studentdashboard.html',sub=sub,l_id=l_id,s_id=s_id)
@app.route('/course')
def  course():
    l_id = request.args.get('l_id')
    s_id = request.args.get('s_id')
    status="Activated"
    db= get_db()
    cur = db.cursor()
    cur.execute('select course_id,course_name,logo from course where status =?',(status,))
    courses=cur.fetchall()
    courses_with_encoded_images = []
    for course in courses:
        course_list = list(course)  # Convert tuple to list
        image_data = course_list[2]
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        course_list[2] = encoded_image  # Modify the list
        courses_with_encoded_images.append(tuple(course_list))
    return render_template('course.html',courses=courses_with_encoded_images,s_id=s_id,l_id=l_id)

@app.route('/enroll')
def  enroll():
    l_id = request.args.get('l_id')
    c_id=request.args.get('c_id')
    s_id = request.args.get('s_id')
    m_no=0
    db= get_db()
    cur = db.cursor()
    cur.execute('select status from enroll_course where course_id= ? and student_id = ? and module_no = ?',(c_id,s_id,m_no))
    status=cur.fetchone()
    cur.execute('select * from course where course_id=?',(c_id,))
    course=cur.fetchone()
    # cur.close()
    encoded_image = base64.b64encode(course[4]).decode('utf-8')
    if status :
        return render_template('enrollcourse.html',course=course,s_id=s_id,img=encoded_image,status=status[0],l_id=l_id)
    else:
        status=''
        return render_template('enrollcourse.html',course=course,s_id=s_id,img=encoded_image,status=status,l_id=l_id)

@app.route('/enrollcourse')
def  enrollcourse():
    l_id = request.args.get('l_id')
    c_id=request.args.get('c_id')
    s_id = request.args.get('s_id')
    m_no=0
    status='ENROLLED'
    date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db= get_db()
    cur = db.cursor()
    print(c_id,s_id,m_no,status)
    cur.execute('INSERT INTO enroll_course(student_id,course_id,module_no,status,enroll_date) values(?,?,?,?,?)',(s_id[0],c_id,m_no,status,date))
    db.commit()
    return redirect(url_for('enroll',s_id=s_id,c_id=c_id,l_id=l_id))

@app.route('/courseinfo')
def  courseinfo():
    l_id = request.args.get('l_id')
    c_id=request.args.get('c_id')
    s_id = request.args.get('s_id')
    db= get_db()
    cur = db.cursor()
    cur.execute('select course_id,course_name,course_description from course where course_id=?',(c_id,))
    course=cur.fetchone()
    cur.execute('''SELECT c.module_no, c.title, e.status FROM course_module c
        LEFT JOIN (SELECT course_id, module_no,status FROM enroll_course
        WHERE student_id = ? GROUP BY course_id, module_no) e 
        ON c.course_id = e.course_id AND c.module_no = e.module_no
        WHERE c.course_id = ?''', (s_id, c_id))
    modules=cur.fetchall()
    f_module=cur.fetchone()
    cur.execute('''SELECT c.module_no, c.title, e.status FROM course_module c
        LEFT JOIN (SELECT course_id, module_no,status FROM enroll_course
        WHERE student_id = ? GROUP BY course_id, module_no) e 
        ON c.course_id = e.course_id AND c.module_no = e.module_no
        WHERE c.course_id = ? ORDER BY c.module_no DESC LIMIT 1''', (s_id, c_id))
    last_module=cur.fetchone()
    cur.execute('SELECT * from assessment where student_id = ? and course_id = ?', (s_id, c_id))
    c_course=cur.fetchone()
    print(c_course)
    print(last_module)
    # cur.close()
    return render_template('courseinfo.html',s_id=s_id,c_course=c_course,course=course,modules=modules,f_module=f_module,last_module=last_module,l_id=l_id)

@app.route('/module_status')
def  module_status():
    l_id = request.args.get('l_id')
    c_id=request.args.get('c_id')
    s_id = request.args.get('s_id')
    m_no=request.args.get('m_no')
    date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db= get_db()
    cur = db.cursor()
 
    cur.execute('select status from enroll_course where course_id= ? and student_id = ? and module_no = ?',(c_id,s_id,m_no))
    status=cur.fetchone()
    if status :
        return redirect(url_for('view_module',s_id=s_id,c_id=c_id,m_no=m_no,l_id=l_id))            
    else:    
        if m_no=="1" :
            status="In Progress"
            cur.execute('INSERT INTO enroll_course(student_id,course_id,module_no,status,enroll_date) values(?,?,?,?,?)',(s_id[0],c_id,m_no,status,date))
            db.commit()
            return redirect(url_for('courseinfo',s_id=s_id,c_id=c_id,l_id=l_id))
        else:
            pre_m_no=str(int(m_no)-1)
            cur.execute('select status from enroll_course where course_id= ? and student_id = ? and module_no = ?',(c_id,s_id,pre_m_no))
            enroll_status=cur.fetchone()
            if enroll_status and enroll_status[0]=="Completed":
                status="In Progress"
                cur.execute('INSERT INTO enroll_course(student_id,course_id,module_no,status,enroll_date) values(?,?,?,?,?)',(s_id[0],c_id,m_no,status,date))
                db.commit()
                return redirect(url_for('view_module',s_id=s_id,c_id=c_id,m_no=m_no,l_id=l_id))
            else:
                sub="courseinfo"

                return render_template('studentdashboard.html',sub=sub,l_id=l_id,c_id=c_id,s_id=s_id)
            
@app.route('/update_module_status')
def  update_module_status():
    l_id=request.args.get('l_id')
    c_id=request.args.get('c_id')
    s_id = request.args.get('s_id')
    m_no=request.args.get('m_no')
    m_status="Completed"
    date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db= get_db()
    cur = db.cursor()
    cur.execute('update enroll_course set status = ? , completed_date= ? where course_id= ? and student_id = ? and module_no = ?',(m_status,date,c_id,s_id,m_no))
    db.commit()
    next_m_no=str(int(m_no)+1)
    cur.execute('select status from enroll_course where course_id= ? and student_id = ? and module_no = ?',(c_id,s_id,next_m_no))
    status=cur.fetchone()
    if status:
        return redirect(url_for('view_module',s_id=s_id,c_id=c_id,m_no=next_m_no,l_id=l_id))            
    else:
        cur.execute('select * from course_module where course_id= ? and module_no = ?',(c_id,next_m_no))
        module=cur.fetchone()
        if module :
           status="In Progress"
           cur.execute('INSERT INTO enroll_course(student_id,course_id,module_no,status,enroll_date) values(?,?,?,?,?)',(s_id[0],c_id,next_m_no,status,date))
           db.commit()
           return redirect(url_for('view_module',s_id=s_id,c_id=c_id,m_no=next_m_no,l_id=l_id))
        else:
           sub="courseinfo"
           return render_template('studentdashboard.html',sub=sub,l_id=l_id,c_id=c_id,s_id=s_id)           
            
@app.route('/view_module')
def  view_module():
    l_id=request.args.get('l_id')
    s_id=request.args.get('s_id')
    c_id=request.args.get('c_id')
    m_no=request.args.get('m_no')
    db= get_db()
    cur = db.cursor()
    cur.execute('select file_path,file_name from course_module where course_id= ? and module_no = ? ',(c_id,m_no))
    pdf=cur.fetchone()
    # cur.close()
    file_path, file_name = pdf
    # pdf_path = os.path.join(file_path, file_name)
    return render_template('module_view.html',pdf_path=file_path,s_id=s_id,c_id=c_id,m_no=m_no,l_id=l_id) 
@app.route('/module_quiz')
def  module_quiz():
    l_id=request.args.get('l_id')
    s_id=request.args.get('s_id')
    c_id=request.args.get('c_id')
    m_no=request.args.get('m_no')
    db= get_db()
    cur = db.cursor()
    cur.execute('select * from module_quiz where course_id=? and module_no =?',(c_id,m_no))
    questions=cur.fetchall()
    print(questions)
    return render_template('module_quiz.html',s_id=s_id,c_id=c_id,m_no=m_no,questions=questions,l_id=l_id) 

@app.route('/final_quiz')
def  final_quiz():
    l_id = request.args.get('l_id')
    s_id=request.args.get('s_id')
    c_id=request.args.get('c_id')
    print(l_id)
    db= get_db()
    cur = db.cursor()
    cur.execute('select * from quiz where course_id=?',(c_id,))
    questions=cur.fetchall()
    return render_template('final_quiz.html',s_id=s_id,c_id=c_id,l_id=l_id,questions=questions) 

@app.route('/final_result',methods=['POST'])
def  final_result():
    l_id = request.args.get('l_id')
    s_id = request.args.get('s_id')
    c_id=request.args.get('c_id')
    score=int(request.form.get('score'))
    total=int(request.form.get('total'))
    m_no=0
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(s_id,c_id,score,total)
    percentage=(score /total)*100
    print(s_id,c_id,score,total,percentage)
    db= get_db()
    cur = db.cursor()
    cur.execute('select * from student where student_id = ?',(s_id,))
    student=cur.fetchone()
    cur.execute('select * from course where course_id = ?',(c_id,))
    course=cur.fetchone()
    cur.execute('insert into assessment (student_id,course_id,student_name,course_name,score_obtained,total_score,percentage,datetime) values(?,?,?,?,?,?,?,?)',(student[0],course[0],student[1],course[1],score,total,percentage,date))
    db.commit()
    cur.execute('update enroll_course set  completed_date=? where course_id= ? and student_id = ? and module_no = ?',(date,c_id,s_id,m_no))
    db.commit()
    # cur.close()
    return redirect(url_for('sd_profile',s_id=s_id,l_id=l_id)) 


@app.route('/sd_mylearning')
def  sd_mylearning():
    l_id = request.args.get('l_id')
    s_id = request.args.get('s_id')
    sub="mylearning"
    return render_template('studentdashboard.html',sub=sub,l_id=l_id,s_id=s_id)
@app.route('/mylearning')
def  mylearning():
    l_id=request.args.get('l_id')
    s_id = request.args.get('s_id')
    m_no=0
    db= get_db()
    cur = db.cursor()
    cur.execute('select course_id,course_name,logo,status from course WHERE course_id IN (SELECT course_id FROM enroll_course WHERE student_id = ? AND module_no = ? )',(s_id,m_no))
    courses=cur.fetchall()
    courses_with_encoded_images = []
    for course in courses:
        course_list = list(course)  # Convert tuple to list
        image_data = course_list[2]
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        course_list[2] = encoded_image  # Modify the list
        courses_with_encoded_images.append(tuple(course_list))
    return render_template('mylearning.html',courses=courses_with_encoded_images,s_id=s_id,l_id=l_id)



@app.route('/sd_enquiries')
def  sd_enquiries():
    l_id = request.args.get('l_id')
    s_id = request.args.get('s_id')
    sub="enquiries"
    return render_template('studentdashboard.html',sub=sub,l_id=l_id,s_id=s_id)
@app.route('/enquiries')
def  enquiries():
    s_id = request.args.get('s_id')
    m_no=0
    db= get_db()
    cur = db.cursor()
    cur.execute('select course_id,course_name from course WHERE course_id IN (SELECT course_id FROM enroll_course WHERE student_id = ? AND module_no = ? )',(s_id,m_no))
    courses=cur.fetchall()
    # cur.close()
    return render_template('enquiries.html',s_id=s_id,courses=courses)
@app.route('/send_message',methods=["POST"])
def  send_message():
    s_id = request.args.get('s_id')
    r_id = request.form.get('receiver-name')
    subject = request.form.get('subject')
    body = request.form.get('body')
    date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(s_id,r_id,subject,body,date_time)
    db= get_db()
    cur = db.cursor()
    cur.execute('select student_id,student_name,email_id from student WHERE student_id =?',(s_id,))
    student=cur.fetchone()
    print(r_id)
    if r_id=="Admin":
        cur.execute('insert into message (sender_email,receiver_email,subject,body,date_time) values(?,?,?,?,?)',(student[2],r_id,subject,body,date_time))
        db.commit()
    else:
        cur.execute('select course_id,course_name from course WHERE course_id =?',(r_id,))
        course=cur.fetchone()
        cur.execute('insert into message (sender_email,receiver_email,subject,body,date_time) values(?,?,?,?,?)',(student[2],course[0],subject,body,date_time))
        db.commit()
    cur.close()
    return redirect(url_for('enquiries',s_id=s_id))

@app.route('/sd_messages')
def  sd_messages():
    l_id = request.args.get('l_id')
    s_id = request.args.get('s_id')
    sub="messages"
    return render_template('studentdashboard.html',sub=sub,l_id=l_id,s_id=s_id)
@app.route('/messages')
def  messages():
    s_id = request.args.get('s_id')
    db= get_db()
    cur = db.cursor()
    cur.execute('select student_id,student_name,email_id from student WHERE student_id =?',(s_id,))  
    student=cur.fetchone()
    cur.execute('select * from message WHERE sender_email = ?',(student[2],))  
    cur.execute('SELECT m.*, c.course_name FROM message m LEFT JOIN course c ON m.receiver_email = c.course_id WHERE m.sender_email = ?', (student[2],))
    s_messages=cur.fetchall()
    cur.execute('SELECT m.*, c.course_name FROM message m LEFT JOIN course c ON m.sender_email = c.course_id WHERE m.receiver_email = ?', (student[2],))
    r_messages=cur.fetchall()
    return render_template('messages.html',s_id=s_id,s_messages=s_messages,r_messages=r_messages)

@app.route('/sd_score')
def  sd_score():
    l_id = request.args.get('l_id')
    s_id = request.args.get('s_id')
    sub="score"
    return render_template('studentdashboard.html',sub=sub,l_id=l_id,s_id=s_id)
@app.route('/score')
def  score():
    s_id = request.args.get('s_id')
    db= get_db()
    cur = db.cursor()
    cur.execute('select * from assessment WHERE student_id =?',(s_id,))  
    scores=cur.fetchall()
    return render_template('score_details.html',s_id=s_id,scores=scores)

if __name__ == "__main__":
    app.run(debug=True)

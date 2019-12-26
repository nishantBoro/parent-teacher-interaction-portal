from flask import Flask, render_template, request, redirect, session, flash, url_for, abort
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)

app.secret_key = "abcasdasdasdas"

# Configure db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register')
def register():
    if session.__contains__('logged_in') and session['logged_in'] is True:
        flash("Action not allowed")
        return redirect(url_for('index'))
    return render_template('registration.html')


@app.route('/login')
def login():
    if session.__contains__('logged_in') and session['logged_in'] is True:
        flash("You are already logged in")
        return redirect(url_for('index'))
    return render_template('login.html')


# def init_default_marks(student_usn):
#     cursor = mysql.connection.cursor()
#     cursor.execute('SELECT ', (student_usn, ))


def get_attendance(selected_student_usn):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT NAME FROM STUDENT WHERE USN = %s', (selected_student_usn,))
    student_row = cursor.fetchone()
    student_name = student_row[0]
    cursor.execute('SELECT * FROM ATTENDANCE WHERE S_USN = %s AND S_SUBJECT_ID IN (SELECT SUBJECT_ID FROM SUBJECT)',
                   (selected_student_usn,))
    all_attendances = cursor.fetchall()
    final_attendance = []
    for (usn, subj_id, attendance) in all_attendances:
        cursor.execute('SELECT SUBJECT_NAME FROM SUBJECT WHERE SUBJECT_ID = %s', (subj_id,))
        subj_name = cursor.fetchone()
        final_attendance.append((subj_name[0], attendance))
    cursor.close()
    return final_attendance, student_name


def get_marks(selected_student_usn):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT NAME FROM STUDENT WHERE USN = %s', (selected_student_usn,))
    student_row = cursor.fetchone()
    student_name = student_row[0]
    cursor.execute('SELECT * FROM MARKS WHERE S_USN = %s AND S_SUBJECT_ID IN (SELECT SUBJECT_ID FROM SUBJECT)',
                   (selected_student_usn,))
    marks = cursor.fetchall()
    final_marks = []
    for (usn, subj_id, cia1, cia2, cia3, assignment, aat, see) in marks:
        cursor.execute('SELECT SUBJECT_NAME FROM SUBJECT WHERE SUBJECT_ID = %s', (subj_id,))
        subj_name = cursor.fetchone()
        final_marks.append((subj_name[0], cia1, cia2, cia3, assignment, aat, see))
    cursor.close()
    return final_marks, student_name


@app.route('/teacher-interacts', methods=['GET', 'POST'])
def teacher_interacts():
    if session['logged_in'] is not True or session['logged_in_as'] != 'Teacher':
        return abort(401)
    data = request.form
    if data['selected-student'] == '0':
        return redirect('/teacher-selects-student')
    if request.method == 'POST' and request.form.get('cia1', 'null') != 'null':
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM SUBJECT')
        subj_list = cursor.fetchall()
        new_marks = []
        new_attendances = []
        selected_student_usn = None
        for idy, row in enumerate(request.form):
            row_data = request.form.getlist(row)
            print(row_data)
            for idx, col in enumerate(row_data):
                if idy == 0:
                    new_marks.append([])
                    new_attendances.append([])
                if idy != len(request.form)-2:
                    new_marks[idx].append(col)
                else:
                    new_attendances[idx].append(col)
        for i in new_attendances:
            print(i)
        for idx, subj in enumerate(subj_list):
            if len(new_marks[idx]) == 6:
                cia1, cia2, cia3, assignment, aat, see = new_marks[idx]
            elif len(new_marks[idx]) == 7:
                cia1, cia2, cia3, assignment, aat, see, selected_student_usn = new_marks[idx]
            cursor.execute('UPDATE MARKS SET CIA1 = %s, CIA2 = %s, CIA3 = %s, ASSIGNMENT = %s, AAT = %s, SEE = %s '
                           'WHERE S_USN = %s AND S_SUBJECT_ID = %s', (cia1, cia2, cia3, assignment, aat, see,
                                                                      selected_student_usn, subj[0]))
            mysql.connection.commit()
            attendance = new_attendances[idx]
            cursor.execute('UPDATE ATTENDANCE SET ATTENDANCE = %s WHERE S_USN = %s AND S_SUBJECT_ID = %s',
                           (attendance, selected_student_usn, subj[0]))
            mysql.connection.commit()
        cursor.close()
        flash('Student data updated successfully!')
        return redirect('/teacher-selects-student')
    selected_student_usn = data['selected-student']
    my_tuple = get_marks(selected_student_usn)
    my_tuple_attendance = get_attendance(selected_student_usn)
    current_marks = my_tuple[0]
    student_name = my_tuple[1]
    current_attendances = my_tuple_attendance[0]
    return render_template('teacher_interacts.html', selected_student_usn=selected_student_usn,
                           student_name=student_name, current_marks=current_marks,
                           current_attendances=current_attendances)


@app.route('/teacher-selects-student', methods=['GET', 'POST'])
def teacher_selects_student():
    if session['logged_in'] is not True or session['logged_in_as'] != 'Teacher':
        return abort(401)
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT USN, NAME FROM STUDENT')
    students = cursor.fetchall()
    cursor.close()
    return render_template('teacher_selects_student.html', students=students)


@app.route('/dashboard-parent')
def dashboard_parent():
    if session['logged_in'] is not True or session['logged_in_as'] != 'Parent':
        return abort(401)
    return render_template('parent_dashboard.html')


@app.route('/dashboard-parent-marks')
def dashboard_parent_marks():
    if session['logged_in'] is not True or session['logged_in_as'] != 'Parent':
        return abort(401)
    usn = session.get("parent_student_usn", None)
    my_tuple = get_marks(usn)
    final_marks = my_tuple[0]
    student_name = my_tuple[1]
    return render_template('parent_dashboard_marks.html', final_marks=final_marks, student_name=student_name)


@app.route('/dashboard-parent-attendance')
def dashboard_parent_attendance():
    if session['logged_in'] is not True or session['logged_in_as'] != 'Parent':
        return abort(401)
    usn = session.get("parent_student_usn", None)
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT NAME FROM STUDENT WHERE USN = %s', (usn,))
    student_row = cursor.fetchone()
    student_name = student_row[0]
    cursor.execute('SELECT * FROM ATTENDANCE WHERE S_USN = %s AND S_SUBJECT_ID IN (SELECT SUBJECT_ID FROM SUBJECT)', (usn,))
    attendance = cursor.fetchall()
    final_attendance = []
    for (usn, subj_id, attendance) in attendance:
        cursor.execute('SELECT SUBJECT_NAME FROM SUBJECT WHERE SUBJECT_ID = %s', (subj_id,))
        subj_name = cursor.fetchone()
        final_attendance.append((subj_name[0], attendance))
    cursor.close()
    return render_template('parent_dashboard_attendance.html', student_name=student_name, final_attendance=final_attendance)


@app.route('/registration-teacher', methods=['GET', 'POST'])
def registration_teacher():
    if session.__contains__('logged_in') and session['logged_in'] is True:
        flash("Action not allowed")
        return redirect(url_for('index'))
    if request.method == 'POST':
        # Fetch form data
        teacher_details = request.form
        name = teacher_details['name']
        email = teacher_details['email']
        password = teacher_details['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO TEACHER(TEACHER_NAME, T_EMAIL, T_PASSWORD) VALUES(%s, %s, %s)", (name, email, password))
        mysql.connection.commit()
        cur.close()
        return redirect('/')
    return render_template('registration_teacher.html')


@app.route('/registration-parent', methods=['GET', 'POST'])
def registration_parent():
    if session.__contains__('logged_in') and session['logged_in'] is True:
        flash("Action not allowed")
        return redirect(url_for('index'))
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        # Fetch form data
        parent_details = request.form
        name = parent_details['name']
        phone_number = parent_details['contact']
        email = parent_details['email']
        password = parent_details['password']
        student = parent_details['selected-student']
        if student == '0':
            flash("Invalid details provided")
            return redirect('/registration-parent')
        cursor.execute("INSERT INTO PARENT(P_NAME, PHONE, EMAIL, P_PASSWORD, S_PICKED_USN) VALUES(%s, %s, %s, %s, %s)",
                       (name, phone_number, email, password, student))
        mysql.connection.commit()
        cursor.execute('UPDATE STUDENT SET REGISTERED = TRUE WHERE USN = %s', (student,))
        mysql.connection.commit()
        cursor.close()
        return redirect('/')
    cursor.execute('SELECT USN, NAME FROM STUDENT WHERE REGISTERED = FALSE')
    students = cursor.fetchall()
    print(students)
    return render_template('registration_parent.html', students=students)


@app.route('/login-teacher', methods=['GET', 'POST'])
def login_teacher():
    if session.__contains__('logged_in') and session['logged_in'] is True:
        flash("You are already logged in")
        return redirect(url_for('index'))
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM TEACHER WHERE T_EMAIL = %s AND T_PASSWORD = %s', (email, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        cursor.close()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['logged_in'] = True
            session['logged_in_as'] = 'Teacher'
            # Redirect to home page
            return redirect('/')
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login_teacher.html', msg=msg)


@app.route('/login-parent', methods=['GET', 'POST'])
def login_parent():
    if session.__contains__('logged_in') and session['logged_in'] is True:
        flash("You are already logged in")
        return redirect(url_for('index'))
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM PARENT WHERE EMAIL = %s AND P_PASSWORD = %s', (email, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        cursor.close()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['logged_in'] = True
            print(session['logged_in'])
            session['logged_in_as'] = 'Parent'
            session['parent_student_usn'] = account[5]
            # Redirect to home page
            return redirect('/')
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login_parent.html', msg=msg)


@app.route('/logout')
def logout():
    if session['logged_in'] is not True and (session['logged_in_as'] != 'Parent' or session['logged_in_as'] != 'Teacher'):
        return abort(401)
    session['logged_in'] = False
    session['logged_in_as'] = None
    return redirect('/')

# @app.route('/users')
# def users():
#     cur = mysql.connection.cursor()
#     resultValue = cur.execute("SELECT * FROM users")
#     if resultValue > 0:
#         userDetails = cur.fetchall()
#         return render_template('users.html',userDetails=userDetails)


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, session
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
    return render_template('registration.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard-teacher')
def dashboardTeacher():
    return render_template('teacher_dashboard.html')

@app.route('/dashboard-parent')
def dashboardParent():
    return render_template('parent_dashboard.html')

@app.route('/registration-teacher', methods=['GET','POST'])
def registrationTeacher():
    if request.method == 'POST':
        # Fetch form data
        teacherDetails = request.form
        name = teacherDetails['name']
        email = teacherDetails['email']
        password = teacherDetails['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO TEACHER(TEACHER_NAME, T_EMAIL, T_PASSWORD) VALUES(%s, %s, %s)",(name, email, password))
        mysql.connection.commit()
        cur.close()
        return redirect('/')
    return render_template('registration_teacher.html')

@app.route('/registration-parent', methods=['GET','POST'])
def registrationParent():
    if request.method == 'POST':
        # Fetch form data
        parentDetails = request.form
        name = parentDetails['name']
        phoneNumber = parentDetails['phone-number']
        email = parentDetails['email']
        password = parentDetails['password']
        student = parentDetails['student-picked']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO PARENT(P_NAME, PHONE, EMAIL, P_PASSWORD, S_PICKED_USN) VALUES(%s, %s, %s)",(name, phoneNumber, email, password, student))
        mysql.connection.commit()
        cur.close()
        return redirect('/')
    return render_template('registration_parent.html')

@app.route('/login-teacher', methods=['GET','POST'])
def loginTeacher():
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

@app.route('/login-parent', methods=['GET','POST'])
def loginParent():
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
            # If account exists in accounts table in out database
            if account:
                # Create session data, we can access this data in other routes
                session['logged_in'] = True
                session['logged_in_as'] = 'Parent'
                # Redirect to home page
                return redirect('/')
            else:
                # Account doesnt exist or username/password incorrect
                msg = 'Incorrect username/password!'
        # Show the login form with message (if any)
        return render_template('login_parent.html', msg=msg)

@app.route('/logout')
def logout():
   # Remove session data, this will log the user out
   session['logged_in'] = False
   session['logged_in_as'] =
   # Redirect to home
   return redirect('/')


/dashboard_teacher
# @app.route('/users')
# def users():
#     cur = mysql.connection.cursor()
#     resultValue = cur.execute("SELECT * FROM users")
#     if resultValue > 0:
#         userDetails = cur.fetchall()
#         return render_template('users.html',userDetails=userDetails)

if __name__ == '__main__':
    app.run(debug=True)
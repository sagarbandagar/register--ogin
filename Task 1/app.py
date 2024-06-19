from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime, timezone

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Root@1234'  # Update this line
app.config['MYSQL_DB'] = 'AiroProfile'

mysql = MySQL(app)

app.secret_key = 'your_secret_key'

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['login_time'] = datetime.now()  # Store naive datetime
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username / password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    if 'loggedin' in session:
        login_time = session.pop('login_time', None)
        if login_time:
            # Ensure login_time is naive datetime
            if login_time.tzinfo is not None and login_time.tzinfo.utcoffset(login_time) is not None:
                login_time = login_time.replace(tzinfo=None)
            session_duration = datetime.now() - login_time
            msg = f'You have been logged in for {str(session_duration)}'
        else:
            msg = 'Error calculating session duration.'
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
    else:
        msg = 'You are not logged in.'
    return render_template('logout.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route("/index")
def index():
    if 'loggedin' in session:
        return render_template("index.html")
    return redirect(url_for('login'))

@app.route("/display")
def display():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template("display.html", account=account)
    return redirect(url_for('login'))

@app.route("/update", methods=['GET', 'POST'])
def update():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE accounts SET username = %s, password = %s, email = %s WHERE id = %s', (username, password, email, session['id']))
            mysql.connection.commit()
            msg = 'You have successfully updated!'
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
        return render_template("update.html", msg=msg)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)

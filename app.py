from flask import Flask, render_template, request, redirect, session
import sqlite3
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "secretkey"

bcrypt = Bcrypt(app)

# Create database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# Home
@app.route('/')
def home():
    return redirect('/login')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
 
        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()

            # SQL Injection Safe Query
            c.execute("INSERT INTO users(username, password) VALUES (?, ?)",
                      (username, hashed_password))

            conn.commit()
            conn.close()

            return redirect('/login')

        except:
            return "Username already exists"

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

        conn.close()
    if user and bcrypt.check_password_hash(user[2], password):

        session['user'] = username
        return redirect('/dashboard')

    else:
        return "Invalid Username or Password"

# Dashboard
@app.route('/dashboard')
def dashboard():

    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])

    return redirect('/login')

# Logout
@app.route('/logout')
def logout():

    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

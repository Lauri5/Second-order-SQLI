import sqlite3
from flask import Flask, request, session, redirect, url_for, render_template, g

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for the session.

# Function to get the SQLite database connection
def get_db():
    if 'db' not in g:  # Check if the connection has not already been opened
        g.db = sqlite3.connect('users.db', check_same_thread=False)  # Database connection
    return g.db

# Function to close the database connection at the end of the application context
@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)  # Removes the connection from the context g
    if db is not None:
        db.close()  # Closes the connection if it exists

# Function to initialize the database
def initialize_db():
    db = get_db()  # Gets the database connection
    db.execute('DROP TABLE IF EXISTS users')  # Drops the users table if it already exists
    db.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
    ''')  # Creates the users table
    db.commit()  # Confirms the changes to the database

# Initialize the database when the application is started
with app.app_context():
    initialize_db()

# Function to generate navigation links
def generate_nav():
    nav_links = '''
    <header>
        <div class="container">
            <ul>
                <li><a href="/">Home</a></li>'''
    if 'username' in session:  # If user is logged in
        nav_links += '''<li><a href="/reset_form">Reset Password</a></li>
                        <li><a href="/logout">Logout</a></li>'''
    else:  # If user is not logged in
        nav_links += '''<li><a href="/register_form">Register</a></li>
                        <li><a href="/login_form">Login</a></li>'''
    nav_links += '''
            </ul>
        </div>
    </header>'''
    return nav_links

# Function to obtain and display the list of registered users in the database
def get_users():
    db = get_db()  # Ensure to get the database connection
    cursor = db.execute('SELECT id, username, password FROM users')  # Executes SQL query to get all users
    users = cursor.fetchall()  # Retrieves all the query results
    user_list = '<h3>Current Users:</h3><ul>'
    for user in users:
        user_list += f'<li>ID: {user[0]}, Username: {user[1]}, Password: {user[2]}</li>'  # Adds each user to the list
    user_list += '</ul>'
    return user_list

# Function to log and execute an SQL query
def log_and_execute(query, args=()):
    db = get_db()  # Ensure to get the database connection
    cursor = db.execute(query, args)  # Executes the query with the provided parameters
    db.commit()  # Confirms the changes to the database
    return cursor

# Route for the home page
@app.route('/')
def home():
    user_data = get_users()  # Gets the user data
    return render_template('base.html', navigation=generate_nav(), content=f'<h1>Welcome to the User Management System</h1>{user_data}')  # Renders the home page

# Route for the registration form
@app.route('/register_form', methods=['GET'])
def register_form():
    user_data = get_users()  # Gets the user data
    form = '''
    <h2>Register User</h2>
    <form method="post" action="/register">
        Username: <input type="text" id="username" name="username" placeholder="Enter your username"><br>
        Password: <input type="password" id="password" name="password" placeholder="Enter your password"><br>
        <input type="submit" value="Register">
    </form>
    '''
    return render_template('base.html', navigation=generate_nav(), content=form + user_data)  # Renders the page with the registration form

# Route to handle user registration
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']  # Retrieves the username from the form
    password = request.form['password']  # Retrieves the password from the form
    log_and_execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))  # Inserts the new user into the database
    return redirect(url_for('home'))  # Redirects to the home page

# Route for the login form
@app.route('/login_form', methods=['GET'])
def login_form():
    user_data = get_users()  # Gets the user data
    form = '''
    <h2>Login</h2>
    <form method="post" action="/login">
        Username: <input type="text" name="username" placeholder="Enter your username"><br>
        Password: <input type="password" name="password" placeholder="Enter your password"><br>
        <input type="submit" value="Login">
    </form>
    '''
    return render_template('base.html', navigation=generate_nav(), content=form + user_data)  # Renders the page with the login form

# Route to handle user login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']  # Retrieves the username from the form
    password = request.form['password']  # Retrieves the password from the form
    cursor = log_and_execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))  # Checks the credentials in the database
    user = cursor.fetchone()  # Retrieves the user if it exists
    if user:
        session['username'] = username  # Sets the session for the user
        return redirect(url_for('home'))  # Redirects to the home page
    else:
        form = '''
        <h2>Login</h2>
        <p>Invalid credentials. Please try again.</p>
        <form method="post" action="/login">
            Username: <input type="text" name="username" placeholder="Enter your username"><br>
            Password: <input type="password" name="password" placeholder="Enter your password"><br>
            <input type="submit" value="Login">
        </form>
        '''
        return render_template('base.html', navigation=generate_nav(), content=form + get_users())  # Renders the login page with an error message

# Route to handle user logout
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)  # Removes the user from the session
    return redirect(url_for('home'))  # Redirects to the home page

# Route for the password reset form
@app.route('/reset_form', methods=['GET'])
def reset_form():
    if 'username' in session:  # Checks if the user is logged in
        user_data = get_users()  # Gets the user data
        form = f'''
        <h2>Reset Password</h2>
        <form method="post" action="/reset" oninput="updateQuery()">
            New Password: <input type="password" id="newPassword" name="newPassword" placeholder="Enter the new password"><br>
            <input type="hidden" id="username" name="username" value="{session['username']}"><br>
            <input type="submit" value="Reset Password">
        </form>
        <h3>Real-Time Query:</h3>
        <p id="live-query"></p>
        '''
        return render_template('base.html', navigation=generate_nav(), content=form + user_data)  # Renders the page with the password reset form
    else:
        return redirect(url_for('login_form'))  # Redirects to the login page if the user is not logged in

# Route to handle the password reset
@app.route('/reset', methods=['POST'])
def reset():
    if 'username' in session:  # Checks if the user is logged in
        new_password = request.form['newPassword']  # Retrieves the new password from the form
        username = session['username']  # Retrieves the username from the session
        query = f"UPDATE users SET password='{new_password}' WHERE username='{username}'"  # Constructs the vulnerable SQL query
        db = get_db()  # Ensure to get the database connection
        db.execute(query)  # Executes the non-parameterized query
        db.commit()  # Confirms the changes to the database
        return redirect(url_for('home'))  # Redirects to the home page
    else:
        return generate_nav() + "You must be logged in to reset the password<br>"

if __name__ == '__main__':
    app.run(debug=True)  # Starts the Flask application in debug mode

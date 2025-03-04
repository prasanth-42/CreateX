from flask import Flask, render_template, request, redirect, url_for, session
import csv
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
USER_CSV = 'users.csv'

# Ensure CSV file exists with headers if not present
def initialize_csv():
    if not os.path.exists(USER_CSV):
        with open(USER_CSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["username", "password"])

# Function to check if username exists
def user_exists(username):
    with open(USER_CSV, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if row[0] == username:
                return True
    return False

# Function to add a new user
def add_user(username, password):
    with open(USER_CSV, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, password])

# Function to validate user credentials
def validate_user(username, password):
    with open(USER_CSV, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if row[0] == username and row[1] == password:
                return True
    return False

@app.route('/')
def home():
    if 'username' in session:
        return f'Welcome, {session["username"]}! <a href="/logout">Logout</a>'
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate_user(username, password):
            session['username'] = username
            return redirect(url_for('home'))
        return 'Invalid credentials. Try again.'
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if user_exists(username):
            return 'Username already exists. Choose another one.'
        add_user(username, password)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    initialize_csv()
    app.run(debug=True)

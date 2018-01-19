from flask import Flask, render_template, redirect, request, session, flash
import re
from mysqlconnection import MySQLConnector
import md5

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
mysql = MySQLConnector(app,'walldb')
app.secret_key="oiwajefoaiwnegwboughuao"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    error = False
    query = "SELECT * FROM users WHERE email = :email"
    emailExists = mysql.query_db(query, request.form)
    if len(request.form['fname']) < 2:
        flash("First Name must be at least 2 characters!", "error") # just pass a string to the flash function
        error = True
    elif not request.form['fname'].isalpha():
        flash("First Name cannot contain numbers!", "error")
        error = True
    if len(request.form['lname']) < 2:
        flash("Last Name must be at least 2 characters!", "error")
        error = True
    elif not request.form['lname'].isalpha():
        flash("Last Name cannot contain numbers!", "error")
        error = True
    if len(request.form['email']) < 1:
        flash("Email cannot be empty!", "error")
        error = True
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!", "error")
        error = True
    if len(emailExists) > 0:
        flash("That email is already taken!", "error")
        error = True
    if len(request.form['password']) < 1:
        flash("Password cannot be empty!", "error")
        error = True
    elif len(request.form['password']) < 8:
        flash("Password must be longer than 8 characters", "error")
        error = True
    if request.form['password'] != request.form['confirmPassword']:
        flash("Passwords don't match!", "error")
        error = True
    if not error:
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        password = md5.new(request.form['password']).hexdigest()
        insert_query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:fname, :lname, :email, :password, NOW(), NOW())"
        query_data = { 'fname': fname, 'lname': lname, 'email': email, 'password': password }
        mysql.query_db(insert_query, query_data)
        session.clear()
        flash("success", "success")
        return redirect('/')

    flash(request.form, "data")

    return redirect('/') # either way the application should return to the index and display the message

@app.route("/login", methods=["POST"])
def login():
    error = False
    if len(request.form['email']) < 1:
        flash("Email cannot be empty!", "error")
        error = True
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!", "error")
        error = True
    if not error:
        email = request.form['email']
        password = md5.new(request.form['password']).hexdigest()
        query = "SELECT * FROM users WHERE email = :email AND password = :password"
        user = mysql.query_db(query, request.form)
        if len(user) > 0:
            flash(request.form, "data")
            session["uid"] = request.form['email']
            return redirect('/wall')
        else:
            flash("Invalid username/password", "error")
    flash(request.form, "data")
    return redirect('/')

@app.route("/wall")
def wall():
    if "uid" in session:
        return render_template("wall.html")
    else:
        return redirect('/')

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')

@app.route("/email/<email>")
def email(email):
    query = "SELECT password FROM users WHERE email = '"+email+"'"
    user = mysql.query_db(query)
    password = "That email didn't exist!"
    if len(user) > 0:
        password = user[0]['password']
    return render_template('email.html', email=email, password=password)


app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
# from flask_wtf import FlaskForm
# from wtforms import StringField,PasswordField,SubmitField
# from wtforms.validators import DataRequired, Email, ValidationError
from flask_bcrypt import Bcrypt
# import bcrypt
import mysql.connector

mysql = mysql.connector.connect(host='localhost', password = 'root@123' , user = 'root', database = 'mydatabase', port = '3306')

if mysql.is_connected():
    print("Connected to MySQL database")

# mycursor = mydb.cursor()

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = 'your_secret_key_here'


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register',methods=['GET' ,'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor = mysql.cursor()
        cursor.execute("SELECT * FROM users where email=%s",(email,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            flash("Email Already Taken")
            return redirect(url_for('register'))
        else:
            cursor = mysql.cursor()
            cursor.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",(name,email,hashed_password))
            mysql.commit()
            cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # if email and password:
        cursor = mysql.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.check_password_hash(user[3], password):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            flash("Login failed. Please check your email and password")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']

        cursor = mysql.cursor()
        cursor.execute("SELECT * FROM users where id=%s",(user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('dashboard.html',user=user[1])
            
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' in session:
        user_id = session['user_id']

        cursor = mysql.cursor()
        cursor.execute("SELECT * FROM users where id=%s",(user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('profile.html',user=user)
            
    return redirect(url_for('login'))

@app.route('/upload',methods=['POST'])
def upload():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = mysql.cursor()
        cursor.execute("SELECT * FROM users where id=%s",(user_id,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            if request.method == 'POST':
                answersheet = request.files['pdf1']
                answersheet.save("static/answersheet.pdf")
                model_answersheet = request.files['pdf2']
                model_answersheet.save("static/model_answersheet.pdf")

                return render_template('results.html',)
    return redirect(url_for('login'))
                              
@app.route('/results')
def results():
    return render_template('results.html', )
if __name__ == '__main__':
    app.run(debug=True)


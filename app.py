from flask import Flask, render_template, request, redirect, session

from database import createTables, AuthQueries
import random
from utils import EmailTemplates, sendEmail
from utils import generateHashPassword, validateHashPassword

app = Flask(__name__)
app.secret_key = "swathi@25"


# Home route
@app.route('/')
def home():
    return render_template('home.html')


# Login
@app.route("/login", methods=['GET', 'POST'])
def login():

    # GET request
    if request.method == 'GET':
        return render_template('login.html')

    # POST request
    # login code here


# Register
@app.route("/register", methods=['GET', 'POST'])
def register():

    # GET request
    if request.method == 'GET':
        return render_template('register.html')

    # POST request
    if request.method == 'POST':

        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        print(name, email, password, confirm_password)

        # Check password and confirm password
        if password != confirm_password:
            print("password miss match")
            return redirect('/register')

        # Check email already exists
        status, msg = AuthQueries.checkEmailExists(email=email)

        if status == True:
            print(msg)
            return redirect('/login')

        print(msg)

        # Generate OTP
        otp = random.randint(1000, 9999)

        # Email body
        body = EmailTemplates.registerEmailTemplate(
            otp=otp,
            username=name
        )

        # Send OTP
        status, msg = sendEmail(
            to_email=email,
            subject="SNS Management Register!!!",
            body=body
        )

        if status == False:
            print(msg)
            return redirect('/register')

        # Store data in session
        session.clear()
        session['otp'] = otp
        session['username'] = name
        session['email'] = email
        session['password'] = password

        # Go to OTP page
        return redirect('/verify-otp')


# Verify OTP
@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():

    if request.method == 'GET':
        return render_template('verify-otp.html')

    # OTP verification code here
    if request.method=='POST':
        otp=int(request.form.get('otp'))
        #matchotp
        if otp != session['otp']:
            print("OTP Incorrect")
            return redirect('/verify-otp')
        hash_password=generateHashPassword(password=session['password'])
        status,msg=AuthQueries.insertUserRecord(username=session['username'],email=session['email'],hash_password=hash_password)

        if status == False:
            print(msg)
            return redirect('/')
        return redirect('/login')




if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)

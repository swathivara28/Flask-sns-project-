from flask import Flask, render_template, request, redirect, session, url_for,send_file,flash

from database import createTables, AuthQueries, NotesQueries, FilesQueries
import random
from utils import EmailTemplates, sendEmail
from utils import generateHashPassword, validateHashPassword
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
import os
from werkzeug.utils import secure_filename
import uuid
from mimetypes import guess_type

app = Flask(__name__)
app.secret_key = "swathi@123"
serializer = URLSafeTimedSerializer(app.secret_key)

if not os.path.exists('uploads'):
    os.mkdir('uploads')

#generateotp
def generateToken(email:str):
    token = serializer.dumps(obj=email,salt="reset-password")
    return token

#validate token
def validateToken(token):
    try:
        data=serializer.loads(token,salt="reset-password",max_age=600)#10mins
        return data
    except BadTimeSignature:
        print("URL Time Expired")
        return redirect('/login')
    except SignatureExpired:
        print("Invalid url")
        return redirect('/login')



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
    
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        status, user = AuthQueries.checkEmailExists(email=email, data=True)

        if status == False:
            flash(user,'msg' if status else 'err')
            return redirect('/login')
        #match password
        status = validateHashPassword(password=password, hash_password=user['hashpassword'])

        if status == False:
            flash("password incorrect",'msg' if status else 'err')
            return redirect('/login')
        #redirect to dashboard page
        session.clear()
        session['id']=user['userid']
        session['username']=user['username']
        return redirect('/dashboard')


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
            flash(msg)
            return redirect('/login')

        flash(msg)

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
            flash(msg)
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

    if request.method == 'POST':
        otp = int(request.form.get('otp'))

        if otp != session['otp']:
            print("OTP Incorrect")
            return redirect('/verify-otp')

        hash_password = generateHashPassword(
            password=session['password']
        )

        status, msg = AuthQueries.insertUserRecord(
            username=session['username'],
            email=session['email'],
            hash_password=hash_password
        )

        if status == False:
            print(msg)
            return redirect('/')

        print(msg)
        return redirect('/login')

#forgot password
@app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')
    if request.method=='POST':
        email=request.form.get('email')
       
        #checkemailexists
        status, msg=AuthQueries.checkEmailExists(email=email)
        if status == False:
            print(msg)
            return redirect(url_for('login'))
        #storeemail in token
        token = generateToken(email=email)
        #generate reset passwrd link
        reset_link =  url_for('reset_password',token=token,_external=True)
         #send link via email
        body= EmailTemplates.forgotPasswordTemplate(url=reset_link)
        status,msg = sendEmail(to_email=email,subject="Reset Password -SNS",body=body)
        if status ==False:
            print(msg)
            return redirect(url_for('forgot_password'))
        #redirect tologin page
        return redirect(url_for('login'))

#reset password
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    email=validateToken(token=token)
    if request.method == 'GET':
        return render_template('reset_password.html',token_val=token)
    if request.method=='POST':
        new_password=request.form.get('new_password')
        confirm_password=request.form.get('confirm_password')
        if new_password != confirm_password:
            print("Password miss match")
            return redirect(url_for('reset_password',token=token))
        #generatehash password
        hash_password=generateHashPassword(password=new_password)
        #update hashpassword in database updates by using email
        status,msg = AuthQueries.updatePassword(email=email,hash_password=hash_password)
        print(msg)
        return f"<h2>{msg}</h2>"

        #return msglike "password updates successfully"

    

#dashboard

@app.route("/dashboard")
def dashboard():
    if 'id' not in session:
        return redirect(url_for('login'))

    userid = session['id']

    # Total Notes count
    status_notes, total_notes = NotesQueries.getNotesCount(userid)

    if not status_notes:
        return str(total_notes), 500

    # Total Files count
    status_files, total_files = FilesQueries.getFilesCount(userid)

    if not status_files:
        return str(total_files), 500

    return render_template(
        "dashboard.html",
        username=session['username'],
        total_notes=total_notes,
        total_files=total_files
    )


#============================================================
#                       Notes Routes
#============================================================
@app.route('/dashboard/notes')
def mynotes():
    if 'id' not in session:
            return redirect('/login')

    userid = session['id']
    status, all_notes = NotesQueries.getAllNotes(userid=userid)
    return render_template('notes.html', notes=all_notes)
## new notes
@app.route('/dashboard/notes/new-notes', methods=['GET', 'POST'])
def new_notes():
    if 'id' not in session:
            return redirect('/login')
   

    if request.method == 'GET':
        return render_template(
            'new_notes.html',
            username=session.get('username')
        )

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        userid = session['id']

        if not title or not content:
            return "Please enter title and content"

        status, message = NotesQueries.insertNotesRecord(
            userid=userid,
            title=title,
            content=content
        )

        if status:
            return redirect('/dashboard/notes')

        return message

    #view notes
    
# View notes
@app.route('/dashboard/notes/view/<int:id>')
def view_notes(id):
    if 'id' not in session:
        return redirect('/login')

    # Get note by notes ID
    status, notes = NotesQueries.getAllNotes(
        userid=session['id'],
        notesid=id
    )
    if not status:
        return str(notes)

    if not notes:
        return "Note not found", 404

    return render_template(
        'view_notes.html',
        note=notes
    )


# Update Note
@app.route('/dashboard/notes/update/<int:notesid>', methods=['GET', 'POST'])
def edit_notes(notesid):
    if 'id' not in session:
        return redirect(url_for('login'))

    userid = session['id']

    if request.method == 'GET':
        status, notes = NotesQueries.getAllNotes(
            userid=userid,
            notesid=notesid
        )

        if not status:
            return str(notes)

        if not notes:
            return "Note not found", 404

        note = notes

        return render_template(
            'edit_notes.html',
            title=note['title'],
            content=note['content'],
            id=notesid
        )

    title = request.form.get('title')
    content = request.form.get('content')

    if not title or not content:
        return "Please enter title and content", 400

    status, msg = NotesQueries.updateNotes(
        userid=userid,
        notesid=notesid,
        title=title,
        content=content
    )

    if status:
        return redirect(url_for('mynotes'))

    return str(msg)


# Delete Note
@app.route('/dashboard/notes/delete/<int:notesid>')
def delete_notes(notesid):
    if 'id' not in session:
        return redirect(url_for('login'))

    status, msg = NotesQueries.deleteNotes(
        userid=session['id'],
        notesid=notesid
    )

    if status:
        return redirect(url_for('mynotes'))

    return str(msg), 500
#==================================================
# View Files
# ==================================================
@app.route('/dashboard/files')
def myfiles():
    if 'id' not in session:
        return redirect(url_for('login'))

    # Get all files based on userid
    status, all_files = FilesQueries.getAllFiles(
        userid=session['id']
    )

    if status:
        return render_template('files.html', files=all_files)

    return str(all_files), 500


@app.route('/dashboard/files/upload_file', methods=['GET', 'POST'])
def upload_file():
    if 'id' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('upload_file.html')

    file = request.files.get('file')

    if not file or file.filename == '':
        return "Please select a file"

    # File metadata
    original_name = file.filename
    file_name = secure_filename(original_name)

    if not file_name or '.' not in file_name:
        return "Invalid filename"

    file_type = file_name.rsplit('.', 1)[-1].lower()

    if file_type not in {'pdf', 'jpg', 'jpeg', 'png', 'docx', 'ppt', 'csv'}:
        return "File type not allowed"

    # Unique filename
    unique_name = str(uuid.uuid1()) + "_" + file_name

    # Create uploads folder
    upload_folder = os.path.join(app.root_path, 'uploads_folder')
    os.makedirs(upload_folder, exist_ok=True)

    # Full file path
    file_path = os.path.join(upload_folder, unique_name)

    # Save uploaded file
    file.save(file_path)

    # Get file metadata
    file_size = os.path.getsize(file_path)
    mime_type = guess_type(file_path)[0]

    data = (
        session['id'],
        original_name,
        unique_name,
        mime_type,
        file_size,
        file_path
    )

    status, msg = FilesQueries.insertFileRecord(file_data=data)

    print(msg)

    if status:
        return redirect(url_for('myfiles'))

    return str(msg), 500


# ==================================================
# View Individual File
# ==================================================

@app.route('/dashboard/files/view/<int:file_id>')
def view_file(file_id):
     #getfile metadata by using file_id
    status,file=FilesQueries.getAllFiles(userid=session['id'], fileid=file_id)
    print(file)
    return send_file(
            path_or_file=file['filepath'],
            mimetype=file['mimetype'],
            as_attachment=False
            )
    
# ==================================================
# Download File
# ==================================================
@app.route('/dashboard/files/download/<int:file_id>')
def download_file(file_id):
    
    #getfile metadata by using file_id
    status,file=FilesQueries.getAllFiles(userid=session['id'], fileid=file_id)
    print(file)
    return send_file(
        path_or_file=file['filepath'],
        mimetype=file['mimetype'],
        as_attachment=True
        )



# ==================================================
# Delete File
# ==================================================
@app.route('/dashboard/files/delete/<int:file_id>')
def delete_file(file_id):
    status,msg=FilesQueries.deleteFile(fileid=file_id)
    print(msg)
    return redirect(url_for('myfiles'))

#logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

#==================================================
#Total Files
#==================================================


# ==================================================
# Run Application
# ==================================================
if __name__ == '__main__':
    print(createTables())
    app.run(debug=True)
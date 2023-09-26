from flask import Flask, render_template, url_for
from flask import redirect, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user
from flask_login import LoginManager, login_required
from flask_login import logout_user, current_user
from datetime import timedelta
import json
import os
import pickle
import writeEmailObjectsToBinaryFile
import writeLogObjectsToBinaryFile
from email import policy
from email.parser import Parser
from werkzeug.security import generate_password_hash, check_password_hash

# Create datbase object, flask app, database path and secret key
db = SQLAlchemy()
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
uri = 'sqlite:///' + os.path.join(basedir, 'database.db')
key = 'thisisasecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SECRET_KEY'] = key

# Create login manager object for managing authentication for current user
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


# Check if a user exists in the database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# User login class
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


# Create database tables for User login
with app.app_context():
    db.init_app(app)
    db.create_all()


@app.route('/', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/', methods=['POST'])
def login_post():
    # login code goes here
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(username=username).first()

    # check if the user actually exists
    # take the user-supplied password, hash it,
    # and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        # if the user doesn't exist or password is wrong,
        # reload the page
        return redirect(url_for('login'))

    # if the above check passes, then we know the user
    # has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('dashboard'))


@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register_post():
    # code to validate and add user to database goes here
    username = request.form.get('username')
    password = request.form.get('password')

    # if this returns a user, then the email already
    # exists in database
    user = User.query.filter_by(username=username).first()

    # if a user is found, we want to redirect back
    # to register page so user can try again
    if user:
        flash('User account already exists')
        return redirect(url_for('register'))

    # create a new user with the form data.
    # Hash the password so the plaintext version isn't saved.
    newUser = User(username=username,
                   password=generate_password_hash(password, method='scrypt'))

    # add the new user to the database
    db.session.add(newUser)
    db.session.commit()

    return redirect(url_for('login'))


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # Set the session parameter and timeout
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)
    pieChartData = writeLogObjectsToBinaryFile.getLogListActionCount(
        'data/logs.bin')
    barChartData = writeLogObjectsToBinaryFile.getLogListTypeCount(
        'data/logs.bin')
    return render_template('dashboard.html',
                           pieChartData=pieChartData,
                           barChartData=barChartData)


@app.route('/emails', methods=['GET'])
@login_required
def emails():
    # Set the session parameter and timeout
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)
    headings = ("ID", "To", "From", "Subject", "Body", "Open")
    emailData = writeEmailObjectsToBinaryFile.readFromBinaryFileToEmailList(
        'data/emails.bin')
    return render_template('emails.html',
                           emailData=emailData,
                           headings=headings)


@app.route('/logs', methods=['GET'])
@login_required
def logs():
    # Set the session parameter and timeout
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)
    headings = ("ID", "Date", "Time", "To", "From",
                "Subject", "Message", "Type", "Action")
    logData = writeLogObjectsToBinaryFile.readFromBinaryFileToLogList(
        'data/logs.bin')
    return render_template('logs.html', logData=logData, headings=headings)


@app.route('/displayEmail/<id>', methods=['GET'])
@login_required
def displayEmail(id):
    # Set the session parameter and timeout
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)
    originalEmail = writeEmailObjectsToBinaryFile.getOriginalEmail(
        id, 'data/emails.bin')

    data = Parser(policy=policy.default).parsestr(originalEmail)

    emailDate = data['date']
    emailTo = data['to']
    emailFrom = data['from']
    emailSubject = data['subject']
    emailBody = data.get_body(preferencelist=('plain')).get_content()
    emailAttachment = "None"
    if (data.get_payload()):
        emailAttachment = data.get_payload()[1]
    emailData = {'Date': emailDate,
                 'To': emailTo,
                 'From': emailFrom,
                 'Subject': emailSubject,
                 'Body': emailBody,
                 'Attachment': emailAttachment}
    # print(emailData)
    return render_template('displayEmail.html', emailData=emailData)


@app.route('/privacypolicy')
def privacypolicy():
    return render_template('privacypolicy.html')


if __name__ == "__main__":
    app.run(host='192.168.1.202', port=9000, debug=False)

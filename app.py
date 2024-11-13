import os
import pprint
from datetime import datetime
from flask import Flask, make_response, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from menu import Menu
from session_manager import SessionManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ussd.sqlite3'
app.config['SECRET_KEY'] = "random string"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
session = SessionManager()
menu = Menu(session)
GLOBAL_RESPONSE = ""

@app.route('/', methods=['POST', 'GET'])
def index():
    """Main menu"""
    session_id = request.values.get("sessionId", None)
    text = request.values.get("text", '')
    user_input = text.split('*')[-1]

    if '*' in text:
        if text.count('*') == 1:
            return menu.home(session_id, user_input)
        elif text.count('*') == 2 and text.startswith('1*'):
            return menu.articles_menu(session_id, user_input)
        elif text.count('*') == 2 and text.startswith('2*'):
            return menu.play_games_menu(session_id, user_input)
        elif text.count('*') == 2 and text.startswith('3*'):
            return menu.send_feedback_menu(session_id, user_input)
        elif text.count('*') == 2 and text.startswith('4*'):
            return menu.admin_menu(session_id, user_input)
    else:
        return menu.home(session_id, text)


def sanitize(phone_number):
    """Helper function that sanitizes phone numbers in international format."""
    if '233' in phone_number:
        if phone_number.index('233') == 0 or phone_number.index('+233') == 0:
            phone_number = phone_number.replace('233', '0').replace('+', '')
    return phone_number

@app.route('/new', methods=['GET', 'POST'])
def new():
    """Form handler for creating new clients"""
    if request.method == 'POST':
        if len(request.form['pin']) != 4:
            flash('Account PIN must be of length 4.')
            return redirect(url_for('new'))

        pprint.pprint(request.form)
        client = Clients(
            name=request.form['name'],
            phone=sanitize(request.form['phone']),
            email=request.form['email_address'],
            balance="0.0",
            pin=request.form['pin'],
            creation_date=datetime.now().strftime('%d/%m/%y %H:%M:%S.%f'))
        db.session.add(client)
        db.session.commit()
        flash('Record was successfully added')
    return render_template('new.html')

@app.route('/new-log', methods=['GET', 'POST'])
def new_log():
    """Form handler for creating new logs"""
    if request.method == 'POST':
        log = Logs(
            timestamp=datetime.now().strftime('%d/%m/%y %H:%M:%S.%f'),
            phone=sanitize(request.form['phone']),
            request_type="Request Callback")
        db.session.add(log)
        db.session.commit()
        flash('Record was successfully added')
    return render_template('new_log.html')

@app.route('/delete', methods=['POST'])
def delete():
    """Allows the admin to delete user data by id."""
    if request.method == 'POST':
        if not request.form['id']:
            flash('Please enter all the fields', 'error')
        else:
            Clients.query.filter_by(id=request.form['id']).delete()
            db.session.commit()
            return redirect(url_for('show_all'))

@app.route('/all')
def show_all():
    """Simple admin page, that shows all registered clients."""
    return render_template('show_all.html', clients=Clients.query.all())

@app.route('/logs')
def show_logs():
    """Page, that shows all requested callbacks."""
    return render_template('show_logs.html', logs=Logs.query.all())

@app.route('/ussd/callback', methods=['POST', 'GET'])
def ussd_callback():
    """USSD callback function, called when trying to access the from USSD channel."""
    _id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", '')

    print(_id, service_code, phone_number, text)

    if text == '':
        return menu.home(_id)
    if text == '1':
        return menu.generate_otp()
    if text[0] == '2' or '2*' == text[0:2]:
        return menu.check_balance_sequence(text, _id, Clients, phone_number)
    if text[0] == '3':
        return menu.request_callback_sequence(text, Logs, _id, phone_number)

    return "END Invalid choice, try again."

if __name__ == '__main__':
    app.run()

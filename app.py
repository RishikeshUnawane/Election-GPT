from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient, ReturnDocument
from pymongo.server_api import ServerApi
from datetime import datetime
import bcrypt

app = Flask(__name__)
app.secret_key = "Abasiandad1213124safa"  # Replace with a strong secret key

#Setting up Cloud DB
# uri = "connection string"
# client = MongoClient(uri, server_api=ServerApi('1'))
# db = client.electiongpt
# users = db.users
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

# Setting up Local DB
client = MongoClient('localhost', 27017)
db = client.electiongpt
users = db.users

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        voter_id = request.form['voterId']

        # Check if the username already exists
        if users.find_one({'username': username}):
            flash('Username already exists. Choose a different one.', 'danger')
        else:
            users.insert_one({
                'username': username,
                'encrypt_pass': hashed,
                'voter_id' : voter_id,
                'user_id': "213234242342",  #needs to be changed 
                'chat_id' : 1,
                'chat_title' : 'New chat',
                'timestamp' : datetime.utcnow(),
                'responses' : []
                })
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password match
        user = users.find_one({'username': username})
        if user:
            if bcrypt.checkpw(request.form['password'].encode('utf-8'), user['encrypt_pass']):
                flash('Login successful.', 'success')
            # Add any additional logic, such as session management
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/populateDB', methods=["GET"])
def populateDB():
    users.insert_one({
        'username' : 'Jhon',
        'encrypt_pass' : 'hello@1$',
        'voter_id' : 'DL/01/001/000000',
        'user_id' : '1234567890123456',
        'chat_id' : '1234567890123432',
        'chat_title' : 'How many seats are there in Lok Sabha?',
        'timestamp' : datetime.utcnow(),
        'responses' : [
        {
        'question' : 'How many seats are there in Lok Sabha?',
        'answer' : 'There are total 545 seats in Lok Sabha'
        }
        ]
    })
    user = users.insert_one({
        'username' : 'Mia',
        'encrypt_pass' : 'hello@1$',
        'voter_id' : 'DL/01/001/000000',
        'user_id' : '1234567820123456',
        'chat_id' : '1234564890123432',
        'chat_title' : 'How many seats are there in Rajya Sabha?',
        'timestamp' : datetime.utcnow(),
        'responses' : [
        {
        'question' : 'How many seats are there in Rajya Sabha?',
        'answer' : 'There are total 288 seats in Rajya Sabha'
        }
        ]
    })
    return "DB updated with sample data!" 

# main driver function
if __name__ == '__main__':
    app.run()

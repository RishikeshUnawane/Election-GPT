from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient, ReturnDocument
from pymongo.server_api import ServerApi
from datetime import datetime
import bcrypt
import uuid

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
chats = db.chats

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
        new_user_id = str(uuid.uuid4())

        # Check if the username already exists
        if users.find_one({'username': username}):
            flash('Username already exists. Choose a different one.', 'danger')
        else:
            users.create_index([("user_Id", 1)])
            chats.create_index([("user_Id", 1)])
            users.insert_one({
                'username': username,
                'encrypt_pass': hashed,
                'voter_id' : voter_id,  
                'user_Id': new_user_id #needs to be changed 
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
            get_userdId = user.get('user_Id')
            if bcrypt.checkpw(request.form['password'].encode('utf-8'), user['encrypt_pass']):
                new_chat = str(uuid.uuid4())
                chats.insert_one({
                    'user_Id' : get_userdId,
                    'chat_Id' : new_chat,
                    'chat_title' : 'How many seats are there in Rajya Sabha?',
                    'timestamp' : datetime.utcnow(),
                    'responses' : [
                    {
                    'question' : 'How many seats are there in Rajya Sabha?',
                    'answer' : 'There are total 288 seats in Rajya Sabha'
                    }]
                })
                user_chats = chats.find({"user_Id": get_userdId}).sort("user_Id", 1)
                for chat in user_chats:
                    print(chat)
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
        'voter_Id' : 'DL/01/001/000000',
        'user_Id' : '1234567890123456',
    })
    user = users.insert_one({
        'username' : 'Mia',
        'encrypt_pass' : 'hello@1$',
        'voter_Id' : 'DL/01/001/000000',
        'user_Id' : '1234567820123456',
    })
    chats.insert_one({
        'user_Id' : '1234567820123456',
        'chat_Id' : '1234564890123432',
        'chat_title' : 'How many seats are there in Rajya Sabha?',
        'timestamp' : datetime.utcnow(),
        'responses' : [
        {
        'question' : 'How many seats are there in Rajya Sabha?',
        'answer' : 'There are total 288 seats in Rajya Sabha'
        }]
    })
    return "DB updated with sample data!" 

# main driver function
if __name__ == '__main__':
    app.run()

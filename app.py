from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from functools import wraps
from pymongo import MongoClient, ReturnDocument
from pymongo.server_api import ServerApi
from datetime import datetime
from langchain_helper import get_qa_chain, create_vector_db
import bcrypt
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = os.getenv("APP_SECRET")  # Replace with a strong secret key

#Setting up Cloud DB
# uri = os.getenv("MONGODB_URI")
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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def register():
    # New user will register and the username and password(hashed) will be saved in the database in the user collection
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        voter_id = request.form['voterId']
        # while registration unique userID is created for the user
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
                'voter_id' : voter_id,  #add voter id validation here
                'user_Id': new_user_id   
                })
            
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        session['username'] = username
        # Check if the username and password match
        user = users.find_one({'username': username})
        if user:
            get_userdId = user.get('user_Id')
            if bcrypt.checkpw(request.form['password'].encode('utf-8'), user['encrypt_pass']):
                new_chat = str(uuid.uuid4())
                chats.insert_one({
                    'user_Id' : get_userdId,
                    'chat_Id' : new_chat,
                    'chat_title' : 'New Chat',
                    'response': [],
                    'timestamp' : datetime.utcnow()
                })
                return redirect(url_for('chat', username=username, user_Id=get_userdId, chat_Id=new_chat))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/chat/<username>/<user_Id>/<chat_Id>', methods=['GET', 'POST'])
@login_required
def chat(username, user_Id, chat_Id):
    
    if request.method == 'POST':
        message_text = request.form['message']
        response = get_qa_chain()(message_text)

        chat_document = chats.find_one({'user_Id': user_Id, 'chat_Id': chat_Id})
        if chat_document:
            update_data = {
                '$set': {
                    'chat_title' : message_text,
                },
                '$push': {
                    'response': {
                        'question': message_text,
                        'answer' : response['result']
                    }  
                }
            }
            chats.update_one({'user_Id': user_Id, 'chat_Id': chat_Id}, update_data)
        
        all_chats = chats.find({'user_Id': user_Id})
        chat_list = list(all_chats)
        updated_document = chats.find_one({'user_Id': user_Id, 'chat_Id': chat_Id})
        chat_history = updated_document['response']
        if updated_document is not None:
            chat_history = updated_document.get('response', [])
        else:
            print("Document not found")
        result_list = []
        for data in chat_history:
            question = data['question']
            answer = data['answer']
            result_list.append((question, answer))
        return render_template('chat.html', username=username, user_Id=user_Id, chat_Id=chat_Id, result_list=result_list, chat_list=chat_list)
    
    all_chats = chats.find({'user_Id': user_Id})
    chat_list = list(all_chats)
    updated_document = chats.find_one({'user_Id': user_Id, 'chat_Id': chat_Id})
    chat_history = updated_document['response']
    result_list = []
    for data in chat_history:
        question = data['question']
        answer = data['answer']
        result_list.append((question, answer))
    
    return render_template('chat.html', username=username, user_Id=user_Id, chat_Id=chat_Id, result_list=result_list, chat_list=chat_list)

@app.route('/newchat/<username>/<user_Id>', methods=['GET'])
@login_required
def newchat(username, user_Id):
    new_chat_Id = str(uuid.uuid4())
    # Insert the new chat into the database
    chats.insert_one({
        'user_Id': user_Id,
        'chat_Id': new_chat_Id,
        'chat_title': 'New Chat',
        'response': [],
        'timestamp': datetime.utcnow()
    })
    # Redirect the user back to the chat page after creating the chat
    return redirect(url_for('chat', username=username, user_Id=user_Id, chat_Id=new_chat_Id))

@app.route('/delete_chat/<username>/<user_Id>/<chat_Id>', methods=['GET', 'POST'])
@login_required
def delete_chat(username, user_Id, chat_Id):
    chat_document = chats.find_one({'user_Id': user_Id, 'chat_Id': chat_Id})
    if chat_document:
        # Delete the chat from the database
        chats.delete_one({'user_Id': user_Id, 'chat_Id': chat_Id})
        flash('Chat deleted successfully.', 'success')
    else:
        flash('Chat not found.', 'danger')
    
    # Redirect back to the chat page
    return redirect(url_for('newchat', username=username, user_Id=user_Id))

@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# main driver function
if __name__ == '__main__':
    app.run(debug=True)

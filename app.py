from flask import Flask, render_template, request, redirect, url_for, flash
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
                    'chat_title' : '',
                    'response': [],
                    'timestamp' : datetime.utcnow()
                })
                return redirect(url_for('chat', username=username, user_Id=get_userdId, chat_Id=new_chat))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/chat/<username>/<user_Id>/<chat_Id>', methods=['GET', 'POST'])
def chat(username, user_Id, chat_Id):
    # chat_history = None
    if request.method == 'POST':
        # user_id = session['user_id']  # Assuming you have user_id stored in session
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
        print('all chat', all_chats)
        updated_document = chats.find_one({'user_Id': user_Id, 'chat_Id': chat_Id})
        chat_history = updated_document['response']
        if updated_document is not None:
            chat_history = updated_document.get('response', [])
            # for chat in chat_history:
            #     print('Chat', chat)
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
    print('all chat', all_chats)
    updated_document = chats.find_one({'user_Id': user_Id, 'chat_Id': chat_Id})
    chat_history = updated_document['response']
    print('updated', updated_document)
    result_list = []
    for data in chat_history:
        question = data['question']
        answer = data['answer']
        result_list.append((question, answer))
    print('result dictionary', result_list)
    return render_template('chat.html', username=username, user_Id=user_Id, chat_Id=chat_Id, result_list=result_list, chat_list=chat_list)

# main driver function
if __name__ == '__main__':
    app.run(debug=True)

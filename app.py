from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient, ReturnDocument
from pymongo.server_api import ServerApi
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

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

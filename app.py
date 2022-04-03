# client = Client(account_sid, auth_token)

# message = client.messages.create(
#     to="+19737229359", 
#     from_="+17579199437",
#     body="Hello from Python!")

# print(message.sid)

from twilio.rest import Client
from flask import Flask, request, redirect, render_template
import random
import os
import pymongo


"""
account_sid = os.getenv('TWILIO_SID')
auth_token  = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)
from_num = "+17579199437"
to_nums = ["+19172266242"]
story = "\nStory time! Reply with a word to continue the story:\n"
"""

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    """loads the page where users can start a game"""
    """
    twilio_num = "+17579199437"
    to_num = "+19172266242"

    account_sid = os.getenv('TWILIO_SID')
    auth_token  = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    client.messages.create(
        to = to_num, 
        from_= twilio_num,
        body = "this is what should send initially")
    """
    return render_template('index.html')


@app.route("/sms", methods=['POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    body = request.values.get('Body', None)
    from_num = request.form.get('From', None)

    #todo: read database to get to_num instead of always sending to jake
    to_num = "+19172266242"
    twilio_num = "+17579199437"

    #todo: update story in database
    #check if sent message is ###: if so the story is over. text full story to all, 

    account_sid = os.getenv('TWILIO_SID')
    auth_token  = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    body = request.values.get('Body', None)

    message = client.messages.create(
	    to = to_num, 
	    from_= twilio_num,
	    body = body)

    return message.sid


@app.route("/create-group", methods=["POST"])
def create_group():
    # gets data from form
    title = request.form['title']
    num_players = request.form['num_players']
    names = request.form.getlist('names')
    nums = request.form.getlist('nums')


    # connects to MongoDB Atlas instance, inserts this game, then closes connection
    with pymongo.MongoClient(os.getenv("DB_CLIENT_STRING")) as client:
        games_table = client.test.games
        new_game = {"title": title, "message": "", "names": names, "nums": nums, "index_in_nums": 0}

        twilio_num = "+17579199437"
        account_sid = os.getenv('TWILIO_SID')
        auth_token  = os.getenv('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)
        for name,to_num in zip(names, nums):
            message = client.messages.create(
	            to = to_num, 
	            from_= twilio_num,
	            body = f"Welcome {name} to game {title}")

        games_table.insert_one(new_game)

    # returns confirmation message
    return f"Game created successfully!"


if __name__ == "__main__":
    app.run(debug=True)
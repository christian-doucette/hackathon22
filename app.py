# client = Client(account_sid, auth_token)

# message = client.messages.create(
#     to="+19737229359",
#     from_="+17579199437",
#     body="Hello from Python!")

# print(message.sid)

from twilio.rest import Client
from flask import Flask, request, redirect, render_template
# from twilio.twiml.messaging_response import MessagingResponse
import random
import os
import pymongo

account_sid = os.getenv('TWILIO_SID')
auth_token  = os.getenv('TWILIO_AUTH_TOKEN')
from_num = "+17579199437"

to_nums = ["+19737229359"]
story = "\nStory time! Reply with a word to continue the story:\n"

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    story += body.split()[0] + " "
    to_num = random.choice(to_nums)
    story = client.messages.create(
	    to = to_num,
	    from_= "+17579199437",
	    body = story)
    return to_num, story

@app.route("/create-group", methods=["POST"])
def create_group():
    # gets data from form
    title = request.form['title']
    num_players = request.form['num_players']
    names = request.form.getlist('names')
    nums = request.form.getlist('nums')


    # connects to MongoDB Atlas instance, inserts this game, then closes connection
    with pymongo.MongoClient(os.getenv('DB_CLIENT_STRING')) as client:
        games_table = client.test.games
        new_game = {"title": title, "message": "", "names": names, "nums": nums, "index_in_nums": 0}
        games_table.insert_one(new_game)

    # returns confirmation message
    return f"Game created successfully!"



if __name__ == "__main__":
    app.run(debug=True)

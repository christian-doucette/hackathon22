# client = Client(account_sid, auth_token)

# message = client.messages.create(
#     to="+19737229359", 
#     from_="+17579199437",
#     body="Hello from Python!")

# print(message.sid)

from twilio.rest import Client
from flask import Flask, request, redirect
# from twilio.twiml.messaging_response import MessagingResponse
import random
import os

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
    twilio_num = "+17579199437"
    to_num = "+19172266242"

    account_sid = os.getenv('TWILIO_SID')
    auth_token  = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    client.messages.create(
        to = to_num, 
        from_= twilio_num,
        body = "this is what should send initially")
    return 'Welcome to Story Time!'

@app.route("/sms", methods=['POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    body = request.values.get('Body', None)
    from_num = request.form.get('From', None)

    #todo: read database to get to_num instead of always sending to jake
    to_num = "+19172266242"
    twilio_num = "+17579199437"

    account_sid = os.getenv('TWILIO_SID')
    auth_token  = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    body = request.values.get('Body', None)

    message = client.messages.create(
	    to = to_num, 
	    from_= twilio_num,
	    body = body)
    return message.sid

if __name__ == "__main__":
    app.run(debug=True)
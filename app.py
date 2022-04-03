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

account_sid = os.getenv('TWILIO_SID')
auth_token  = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)
from_num = "+17579199437"

<<<<<<< HEAD
to_nums = ["+19737229359"]
=======
to_nums = ["+19172266242"]
>>>>>>> 29e3598997f82d407b0840ff47257cdfb3edf415
story = "\nStory time! Reply with a word to continue the story:\n"

app = Flask(__name__)

@app.route('/')
def hello():
<<<<<<< HEAD
=======
    to_num = random.choice(to_nums)
    story = client.messages.create(
        to = to_num, 
        from_= from_num,
        body = story)
>>>>>>> 29e3598997f82d407b0840ff47257cdfb3edf415
    return 'Welcome to Story Time!'

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    story += body.split()[0] + " "
    to_num = random.choice(to_nums)
<<<<<<< HEAD
    story = client.messages.create(
	    to = to_num, 
	    from_= "+17579199437",
=======
    message = client.messages.create(
	    to = to_num, 
	    from_= from_num,
>>>>>>> 29e3598997f82d407b0840ff47257cdfb3edf415
	    body = story)
    return to_num, story

if __name__ == "__main__":
<<<<<<< HEAD
    app.run(debug=True)
=======
    app.run(debug=True)
>>>>>>> 29e3598997f82d407b0840ff47257cdfb3edf415

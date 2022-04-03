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

account_sid = "ACc0bb41c45abdc570fb0d70cc670085bf"
auth_token  = "2cd3f31b24588565f367671f415487bd"
from_num = "+17579199437"

to_nums = ["+19737229359"]
story = "\nStory time! Reply with a word to continue the story:\n"

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    story += body.split()[0]
    to_num = random.choice(to_nums)
    story = client.messages.create(
	    to = to_num, 
	    from_= "+17579199437",
	    body = story)
    return to_num, story

if __name__ == "__main__":
    app.run(debug=True)
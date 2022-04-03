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
    return render_template('index.html')


@app.route("/sms", methods=['POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    body = request.values.get('Body', None).split()[0]
    from_num = request.form.get('From', None)

    # scans database to get the row for the game involving this number
    with pymongo.MongoClient(os.getenv("DB_CLIENT_STRING")) as db_client:
        games_table = db_client.test.games
        game_info = None 

        rows = games_table.find({})
        for row in rows:
            if from_num in row["nums"]:
                game_info = row 
                break




    twilio_num = "+17579199437"

    #todo: update story in database
    #check if sent message is ###: if so the story is over. text full story to all, 

    account_sid = os.getenv('TWILIO_SID')
    auth_token  = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)


    if game_info is None:
        message = client.messages.create(
            to = from_num, 
            from_= twilio_num,
            body = "You're not currently in a Story. Please contact Jake Apfel. Please.")
        return 400

    elif body == "END":
        #game is ending. text everyone full story and remove database entry

        #todo: check if is players turn. can only end if is their turn
        for to_num in game_info["nums"]:
            message = client.messages.create(
                to = to_num, 
                from_= twilio_num,
                body = game_info["message"])

        with pymongo.MongoClient(os.getenv("DB_CLIENT_STRING")) as db_client:
            games_table = db_client.test.games
            games_table.delete_one({"_id": game_info["_id"]})
        return 200


    else:
        #recieved a non command message. add to the story if it is this players turn

         #todo: check if is players turn. can only add message if is players
        game_info["message"] = game_info["message"] + " " + body
        game_info["index_in_nums"] = (game_info["index_in_nums"] + 1) % len(game_info["nums"])

        message = client.messages.create(
            to = game_info["nums"][game_info["index_in_nums"]], 
            from_= twilio_num,
            body = game_info["message"])

        with pymongo.MongoClient(os.getenv("DB_CLIENT_STRING")) as db_client:
            games_table = db_client.test.games
            games_table.update_one({"_id": game_info["_id"]}, {"$set": game_info})
        return 200




@app.route("/create-group", methods=["POST"])
def create_group():
    # gets data from form
    title = request.form['title']
    num_players = request.form['num_players']
    names = request.form.getlist('names')
    nums = request.form.getlist('nums')
    # adds +1 to start of phone number and removes dashes
    nums = [f'+1{num.replace("-", "")}' for num in nums]


    # connects to MongoDB Atlas instance, inserts this game, then closes connection
    with pymongo.MongoClient(os.getenv("DB_CLIENT_STRING")) as db_client:
        games_table = db_client.test.games
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
from twilio.rest import Client
from flask import Flask, request, redirect, render_template
import random
import os
import pymongo


app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello():
    return render_template('index.html')


@app.route('/rules', methods=['GET'])
def rules():
    return render_template('rules.html')


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
    account_sid = os.getenv('TWILIO_SID')
    auth_token  = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    if game_info is None:
        message = client.messages.create(
            to = from_num, 
            from_= twilio_num,
            body = "You're not currently in a story. Visit https://story-time-hackathon.herokuapp.com/ to start a new story.")
        return "400"

    cur_num = game_info["nums"][game_info["index_in_nums"]]
    if cur_num != from_num:
        message = client.messages.create(
            to = from_num, 
            from_= twilio_num,
            body = "It's not your turn! Wait for the story to come to you.")
        return "400"

    if body == "*":
        #pick sign off
        sign_off = random.choice(["Are movie rights available for that?", "What a fun story...", "I could write a better story. And I'm not even real.", "HAHAHAHA", "That made me smile.", "That made me tear up.", "Thanks for playing :)", "Better luck next time."])
        length = len(game_info["message"])
        if length < 20:
            sign_off = random.choice(["Really? That's it?", sign_off])
        elif length > 120:
            sign_off = random.choice(["Too long; didn't read.", sign_off])

        #game is ending. text everyone full story and remove database entry
        for to_num in game_info["nums"]:
            message = client.messages.create(
                to = to_num, 
                from_= twilio_num,
                body = f"Your completed story \'{game_info['title']}\' is:\n\n" + game_info["message"] + "\n\n" + sign_off)

        with pymongo.MongoClient(os.getenv("DB_CLIENT_STRING")) as db_client:
            games_table = db_client.test.games
            games_table.delete_one({"_id": game_info["_id"]})
        return "200"

    else:
        #recieved a non command message. add to the story if it is this players turn
        game_info["message"] = game_info["message"] + body + " "
        game_info["index_in_nums"] = (game_info["index_in_nums"] + 1) % len(game_info["nums"])

        message = client.messages.create(
            to = game_info["nums"][game_info["index_in_nums"]], 
            from_= twilio_num,
            body = f"The current story \'{game_info['title']}\' is:\n\n" + game_info["message"] + "\n\nReply with a word to continue the story or \'*\' to end it.")

        with pymongo.MongoClient(os.getenv("DB_CLIENT_STRING")) as db_client:
            games_table = db_client.test.games
            games_table.update_one({"_id": game_info["_id"]}, {"$set": game_info})
        return "200"


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
        for name,to_num in list(zip(names, nums))[1:]:
            message = client.messages.create(
                to = to_num, 
                from_= twilio_num,
                body = f"{name}, welcome to story \'{title}\'! Reply with a word once the story comes to you.")
        message = client.messages.create(
            to = nums[0], 
            from_= twilio_num,
            body = f"{names[0]}, welcome to story \'{title}\'! Reply with a word to begin the story.")

        games_table.insert_one(new_game)

    # returns confirmation message
    return render_template('create_game.html')


if __name__ == "__main__":
    app.run(debug=True)
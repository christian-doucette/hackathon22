from twilio.rest import Client
from flask import Flask, request, redirect, render_template
import random
import os
import pymongo


app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello():
    return render_template('index.html')


@app.route('/about_us', methods=['GET'])
def rules():
    return render_template('about_us.html')


@app.route("/sms", methods=['POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    body = request.values.get('Body', None).split()
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

    body = body[:game_info['max_words']]
    ended = False
    for word in body:
        if word == "*":
            ended = True
            break
        game_info["message"] += word + " "

    if ended:
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
        game_info["index_in_nums"] = (game_info["index_in_nums"] + 1) % len(game_info["nums"])

        if game_info['max_words'] == 1:
            body = f"The current story \'{game_info['title']}\' is:\n\n" + game_info["message"] + f"\n\nReply with a word to continue the story or \'*\' to end it."
        else:
            body = f"The current story \'{game_info['title']}\' is:\n\n" + game_info["message"] + f"\n\nReply with up to {game_info['max_words']} words to continue the story or \'*\' to end it."

        message = client.messages.create(
            to = game_info["nums"][game_info["index_in_nums"]],
            from_= twilio_num,
            body = body)

        with pymongo.MongoClient(os.getenv("DB_CLIENT_STRING")) as db_client:
            games_table = db_client.test.games
            games_table.update_one({"_id": game_info["_id"]}, {"$set": game_info})
        return "200"


@app.route("/create-group", methods=["POST"])
def create_group():
    # gets data from form
    title = request.form['title']
    num_players = request.form['num_players']
    max_words = int(request.form['max_words'])
    names = request.form.getlist('names')
    nums = request.form.getlist('nums')
    # adds +1 to start of phone number and removes dashes
    nums = [f'+1{num.replace("-", "")}' for num in nums]
    str_names = ', '.join([name for name in names])

    # connects to MongoDB Atlas instance, inserts this game, then closes connection
    with pymongo.MongoClient(os.getenv("DB_CLIENT_STRING")) as db_client:
        games_table = db_client.test.games

        # checking if any player is already in a story. if so, story creation fails
        rows = games_table.find({})
        for row in rows:
            if len(set(row["nums"]) & set(nums)) > 0:
                return render_template("create_game_fail.html")

        new_game = {"title": title, "message": "", "names": names, "nums": nums, "index_in_nums": 0, "max_words": max_words}
        twilio_num = "+17579199437"
        account_sid = os.getenv('TWILIO_SID')
        auth_token  = os.getenv('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)

        if max_words == 1:        
            body = f"{name}, welcome to story \'{title}\'! Reply with a word once the story comes to you. You are playing with {names}"
        else:    
            body = f"{name}, welcome to story \'{title}\'! Reply with up to {max_words} words once the story comes to you. You are playing with {names}"

        for name,to_num in list(zip(names, nums))[1:]:
            message = client.messages.create(
                to = to_num,
                from_= twilio_num,
                body = body)

        if max_words == 1:
            body = f"{names[0]}, welcome to story \'{title}\'! Reply with a word to begin the story."
        else:
            body = f"{names[0]}, welcome to story \'{title}\'! Reply with up to {max_words} words to begin the story."

        message = client.messages.create(
            to = nums[0],
            from_= twilio_num,
            body = body)

        games_table.insert_one(new_game)

    # returns confirmation message
    return render_template('create_game.html')


if __name__ == "__main__":
    app.run(debug=True)

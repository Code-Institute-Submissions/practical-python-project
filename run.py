import os
import json
from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

def write_to_file(filename, data):
    """Write data to a file"""
    with open(filename, "a") as file:
        file.writelines(data)

def is_correct(guess, answer):
    if (answer == guess):
        return True

def increment_score(username, score):
    new_score = score + 1
    update_score(username, new_score)
    return new_score

def submit_guess(username, score, guess, answer):
    if is_correct(guess, answer):
        increment_score(username, score)
    else:
        timestamp = datetime.now().strftime("%H:%M:%S")
        incorrect_guess = "{0} incorrectly guessed {1} at {2}... shame".format(username, guess, timestamp)
        update_guesses(incorrect_guess, score)
    return score

def add_user(username):
    with open("data/users.txt", "r") as f:
        users = json.loads(f.read())
        users[username] = 0
    with open("data/users.txt", "w") as f:
        f.write(json.dumps(users, sort_keys=True, indent=4, separators=(',', ': ')))

def update_score(username, score):
    with open("data/users.txt", "r+") as f:
        users = json.loads(f.read())
        users[username] = str(score)
    with open("data/users.txt", "w+") as f:
        f.write(json.dumps(users, sort_keys=True, indent=4, separators=(',', ': ')))
    return score

def update_guesses(incorrect_guess, score):
    with open("data/guesses.txt", "r") as f:
        users = json.loads(f.read())
        users.update({incorrect_guess : score})
    with open("data/guesses.txt", "w+") as f:
        f.write(json.dumps(users, sort_keys=True, indent=4, separators=(',', ': ')))

def update_leaderboard(users, number_of_riddles):
    leaderboard_list = []
    for i in range(number_of_riddles,-1,-1):
        for key, value in users.items():
            if int(value) == i:
                """Let's append this to an empty list and print the whole list at the end"""
                user_highscore = "{0}: {1}\n".format(key, value)
                leaderboard_list.append(user_highscore)
                with open("data/leaderboard.txt", "w") as leaderboard:
                    leaderboard.writelines(leaderboard_list)

def get_answer(score, riddles):
    for question in riddles:
        if question['index'] == score:
            return question['answer']

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page with instructions for playing redirects to username url"""
    if request.method == "POST":
        username = request.form["username"]
        add_user(username)
        return redirect(username)
    return render_template("index.html")

@app.route('/<username>', methods=['GET', 'POST'])
def playgame(username):
    with open("data/users.txt", "r") as f:
        users = json.loads(f.read())
        score = int(users[username])
    with open("data/guesses.txt", "r") as guesses:
        guesses = json.loads(guesses.read())
    with open("data/riddles.json", "r") as riddles_data:
        riddles = json.load(riddles_data)
        number_of_riddles = len(riddles)
    answer = get_answer(score, riddles)
    if request.method == "POST":
        submit_guess(username, score, request.form["guess"], answer)
        update_leaderboard(users, number_of_riddles)
        return redirect(username)
    if score < number_of_riddles:
        return render_template("riddles.html", riddles=riddles, score=score, guesses=guesses)
    else:
        return redirect('/completed')

@app.route('/completed')
def completed():
    return render_template("completed.html")

@app.route('/leaderboard')
def leaderboard():
    leaderboard = [line.rstrip('\n') for line in open('data/leaderboard.txt')]
    print(leaderboard)
    return render_template("leaderboard.html", leaderboard=leaderboard)

if __name__ == '__main__':
    app.run(debug=True)


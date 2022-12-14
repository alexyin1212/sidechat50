import os
# import json so that it can be used with ajax to receive data from js
import json
import cs50

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = cs50.SQL("sqlite:///users.db")
db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL)")
db.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, post TEXT NOT NULL, likes INTEGER NOT NULL DEFAULT(0), 'time' DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id))")
db.execute("CREATE TABLE IF NOT EXISTS liked (post_id INTEGER NOT NULL, user_id INTEGER NOT NULL, FOREIGN KEY(post_id) REFERENCES posts(id), FOREIGN KEY(user_id) REFERENCES users(id))")
db.execute("CREATE TABLE IF NOT EXISTS disliked (post_id INTEGER NOT NULL, user_id INTEGER NOT NULL, FOREIGN KEY(post_id) REFERENCES posts(id), FOREIGN KEY(user_id) REFERENCES users(id))")



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# displays the login screen for the user
@app.route("/")
@login_required
def index():   
    # gets the session id of the user, all the posts from the database, as well as the liked posts of the current user
    id = session["user_id"]
    posts = db.execute("SELECT * FROM posts ORDER BY time DESC")
    liked = db.execute("SELECT post_id FROM liked WHERE user_id = ?", id)
    disliked = db.execute("SELECT post_id FROM disliked WHERE user_id = ?", id)
    # create lists and adds all the liked and disliked posts of this user to them
    likes = []
    dislikes = []
    for post in liked:
        likes.append(post["post_id"])

    for post in disliked:
        dislikes.append(post["post_id"])

    return render_template("index.html", posts=posts, likes=likes, dislikes=dislikes)

# Display index by votes descending
@app.route("/top")
@login_required
def top():   
    id = session["user_id"]
    # just like the index page but the votes are grabed in likes descending order from database
    posts = db.execute("SELECT * FROM posts ORDER BY likes DESC")
    liked = db.execute("SELECT post_id FROM liked WHERE user_id = ?", id)
    disliked = db.execute("SELECT post_id FROM disliked WHERE user_id = ?", id)
    likes = []
    dislikes = []
    for post in liked:
        likes.append(post["post_id"])

    for post in disliked:
        dislikes.append(post["post_id"])

    return render_template("index.html", posts=posts, likes=likes, dislikes=dislikes)


@app.route("/likes", methods=["GET", "POST"])
@login_required
def likes():
    # checks for the post from ajax
    if request.method == "POST":
        # create an empty dict
        data = {}
        # grab the data from ajax and place them into the dict we created 
        data["id"] = request.json["post_id"]
        data["likes"] = int(request.json["likes"])
        data["user_id"] = request.json["user_id"]
        db.execute("UPDATE posts SET likes = ? WHERE id = ?", data["likes"], data["id"])
        data["status"] = request.json["status"]
        # get all the liked and disliked posts of the user from the database
        liked = db.execute("SELECT * FROM liked WHERE post_id = ? AND user_id = ?", data["id"], data["user_id"])
        disliked = db.execute("SELECT * FROM disliked WHERE post_id = ? AND user_id = ?", data["id"], data["user_id"])
        # if the user clicked on the like button
        if data["status"] == "liked":
                # if the post is already liked by the user
                if liked:
                    # remove the user-post pair from the liked database
                    db.execute("DELETE FROM liked WHERE post_id = ? AND user_id = ?", data["id"], data["user_id"])
                # if the post is already disliked by the user
                elif disliked:
                    # remove the user-post pair from the disliked database and add the pair to the liked database
                    db.execute("DELETE FROM disliked WHERE post_id = ? AND user_id = ?", data["id"], data["user_id"])
                    db.execute("INSERT INTO liked (post_id, user_id) VALUES (?, ?)", data["id"], data["user_id"])
                # if no button is currently on
                else:
                    # add the pair to the liked database
                    db.execute("INSERT INTO liked (post_id, user_id) VALUES (?, ?)", data["id"], data["user_id"])
        # if the user clicked on the disliked button
        else:
                # if the post is already disliked by the user
                if disliked:
                    # remove the user-post pair from the disliked database
                    db.execute("DELETE FROM disliked WHERE post_id = ? AND user_id = ?", data["id"], data["user_id"])
                # if the post is already liked by the user
                elif liked:
                    # remove the user-post pair from the liked database and add the pair to the disliked database
                    db.execute("DELETE FROM liked WHERE post_id = ? AND user_id = ?", data["id"], data["user_id"])
                    db.execute("INSERT INTO disliked (post_id, user_id) VALUES (?, ?)", data["id"], data["user_id"])
                # if no button is currently on
                else:
                    # add the pair to the disliked database
                    db.execute("INSERT INTO disliked (post_id, user_id) VALUES (?, ?)", data["id"], data["user_id"])

        return redirect("/")
    else:
        return redirect("/")


# displays all posts made by current user
@app.route("/my_posts")
@login_required
def my_posts():
    # get all the data relevent from the databases
    id = session["user_id"]
    posts = db.execute("SELECT * FROM posts WHERE user_id = ? ORDER BY time DESC", id)
    # get the liked and disliked posts from by the user
    liked = db.execute("SELECT post_id FROM liked WHERE user_id = ?", id)
    disliked = db.execute("SELECT post_id FROM disliked WHERE user_id = ?", id)
    likes = []
    dislikes = []
    # change the list of dicts into lists of post_id
    for post in liked:
        likes.append(post["post_id"])

    for post in disliked:
        dislikes.append(post["post_id"])
    # pass the data to the profile page
    return render_template("my_posts.html", posts=posts, likes=likes, dislikes=dislikes)


# displays page for user to create a post
@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    # check to see if the user is submitting a post
    if request.method == "POST":
        id = session["user_id"]
        post = request.form.get("post")
        # insert the new post into the database
        db.execute("INSERT INTO posts (user_id, post) VALUES (?, ?)", id, post)
        return redirect("/")
    # return the posting page
    else:
        return render_template("post.html")


# shows user profile which contains hyperlinks to change password and usernam
@app.route("/profile")
@login_required
def profile():
    # gets the current user's username from teh database
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]['username']
    # gets the user's number of karma received 
    karma = db.execute("SELECT SUM(likes) AS k FROM posts WHERE user_id = ?", session["user_id"])
    return render_template("profile.html", username=username, karma=karma[0]["k"])


# displays page allowing users to send feedback to us developers
@app.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    return render_template("feedback.html")


# displays login page for the user
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# signs the user out 
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username is blank or existing
        username = request.form.get("username")
        existing_users = db.execute("SELECT username FROM users")
        if not username:
            return apology("must type in a username!")
        elif username in [user["username"] for user in existing_users]:
            return apology("this username already exists")

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # check if passwords are blank and are matching
        if not password or not confirmation:
            return apology("must type in password")
        elif password != confirmation:
            return apology("passwords must match")

        # hash the password and insert username and password into database
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed_password)
        session["background_color"] = ""

        return redirect("/login")

    if request.method == "GET":
        return render_template("register.html")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")
        # check if passwords are blank and are matching
        if not new_password or not confirmation:
            return apology("must type in password")
        elif new_password != confirmation:
            return apology("passwords must match")

        # hash the password and insert username and password into database
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hashed_password, session["user_id"])
        return redirect("/login")

    # return the form to submit new password
    if request.method == "GET":
        return render_template("change_password.html")


@app.route("/change_username", methods=["GET", "POST"])
@login_required
def change_username():
    # check to see if user is submitting data
    if request.method == "POST":
        new_username = request.form.get("new_username")
        confirmation = request.form.get("confirmation")
        # check if username is null
        if not new_username or not confirmation:
            return apology("must type in a username!")
        # check if confirmation and new username match
        if new_username != confirmation:
            apology("usernames don't match")
        current_username = db.execute("SELECT username FROM users")
        # check if new username is the same as old username
        if new_username == current_username:
            apology("Your new username is the same as your old ")
        existing_users = db.execute("SELECT username FROM users")
        # check if new username already exists in the database
        if new_username in [user["username"] for user in existing_users]:
            return apology("this username already exists")
        # if everything checks out then update the username in the database
        db.execute("UPDATE users SET username = ? WHERE id = ?", new_username, session["user_id"])
        return redirect("/")

    # return the form to submit new username
    if request.method == "GET":
        return render_template("change_username.html")

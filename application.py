import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from validate_email import validate_email
import requests
import urllib.parse
from functools import wraps

import datetime
from datetime import timedelta


# Configuring application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)

db = SQL("sqlite:///quiz.db")

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

msg = None

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    details = db.execute("SELECT username, score FROM users WHERE type = ? ORDER BY score DESC, time ASC", "user")
    msg = request.args.get("msg")
    if msg:
        return render_template("index.html", details=details, msg = msg)
    return render_template("index.html", details=details)

app.config['SECRET_KEY'] = 'the random string'


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    session.clear()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["type"] = rows[0]["type"]

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        if rows[0]["type"] == 'user':
            return redirect("/")
        else:
            return redirect("/admin")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        username = request.form.get("username")
        mail = request.form.get("mail")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not mail:
            return apology("must provide mail id", 400)
        elif not confirmation:
            return apology("must provide password again", 400)
        elif "@student.tce.edu" not in mail:
            return apology("must provide tce mail id", 400)

        users = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(users) != 0:
            return apology("username already exists", 400)

        if password != confirmation:
            return apology("passwords do not match", 400)

        register = db.execute("INSERT INTO users (username, hash, mail, type) VALUES (?, ?, ?, ?)", username, generate_password_hash(password), mail, "user")
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["type"] = "user"
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:
        return render_template("register.html")


x = datetime.datetime.now()


@app.route("/question", methods=["GET", "POST"])
@login_required
def question():

    if request.method == "GET":
        if "done" not in session:
            session["done"] = []
        if session["user_id"] in session["done"]:
            msg = "You have already attempted today's question"
            return redirect(url_for('index', msg = msg))
        msg = "Please submit a answer"
        question = db.execute("SELECT question FROM qa WHERE date = ?", x)
        return render_template("question.html", question=question, msg = msg)

    if request.method == "POST":
        answer = request.form.get("answer")
        msg = "Answer Submitted!"
        ans = db.execute("SELECT answer FROM qa WHERE date =?", x)
        ans = ans[0]["answer"]
        time = db.execute("UPDATE users SET time = ? WHERE id = ?", x, session["user_id"])
        user_score = db.execute("SELECT score FROM users WHERE id = ?", session["user_id"])
        user_score = user_score[0]["score"]

        if answer == ans:
            update = db.execute("UPDATE users SET score = ? WHERE id = ?", user_score + 10, session["user_id"])
            done = session["done"]
            idvalue = session["user_id"]
            done.append(idvalue)
            session['done'] = done

        return render_template("question.html", msg = msg)

@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    details = db.execute("SELECT * FROM qa")
    if request.method == "GET":
        return render_template("admin.html", details=details)
    if request.method == "POST":
        question = request.form.get("question")
        date = request.form.get("date")
        answer = request.form.get("answer")

        if not question:
            return apology("must provide question", 400)
        elif not date:
            return apology("must provide date", 400)
        elif not answer:
            return apology("must provide answer", 400)

        dates = db.execute("SELECT * FROM qa WHERE date = ?", date)
        if len(dates) != 0:
            return apology("question already exists", 400)
        x = datetime.datetime.now()
        insert = db.execute("INSERT INTO qa (question, answer, date, time) VALUES (?, ?, ?, ?)", question, answer, date, x)

        return redirect("/admin")

@app.route("/pqa", methods=["GET", "POST"])
def pqa():
    x = datetime.datetime.now()
    details = db.execute("SELECT * FROM qa WHERE date < ?", x)
    return render_template("pqa.html", details=details)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
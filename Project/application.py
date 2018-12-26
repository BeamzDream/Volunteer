import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import smtplib

from helper import apology, login_required, login_org_required
from math import sin, cos, sqrt, atan2, radians

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

UPLOAD_FOLDER = "static/Profilepics"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
dbv = SQL("sqlite:///Volunteer.db")
dbc = SQL("sqlite:///Charity.db")

# Homepage


@app.route("/")
@login_required
def index():
    return render_template("index.html")
# Homepage for both volunteer and charity but different header due to session ID leading to different pages


@app.route("/org")
@login_org_required
def org():
    return render_template("index.html")
# Main register page where user is asked to choose if volunteer or charity


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("type"):
            return apology("Please select input")
        if request.form.get("type") == 'volunteer':
            return redirect("/registerstu")
        elif request.form.get("type") == 'organization':
            return redirect("/registerorg")
    else:
        return render_template("register.html")
# If registrant is a volunteer, lead to first page of registration for volunteers asking personal details as well as username and password (hashed) and insert into volunteer database


@app.route("/registerstu", methods=["GET", "POST"])
def registerstu():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("name") or not request.form.get("birthday") or not request.form.get("phone") or not request.form.get("email") or not request.form.get("lat") or not request.form.get("long"):
            return apology("Missing Personal Information Inputs")
        elif not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Make sure your username and password are input into their fields")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords don't match")
        id = dbv.execute("INSERT INTO profiles (name, birthday, phone, email, username, hash, location_lat, location_long) VALUES(:name, :birthday, :phone, :email, :username, :hash, :lat, :long)", name=request.form.get("name"), lat=request.form.get(
            "lat"), long=request.form.get("long"), birthday=request.form.get("birthday"), phone=request.form.get("phone"), email=request.form.get("email"), username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))
        if not id:
            return apology("Username is already taken")
        session["user_id"] = id
        return redirect("/registerstu2")
    else:
        return render_template("registerstu.html")
# Second page of registration for volunteers where user submits profile picture. If they don't, predefined one will be used.


@app.route("/registerstu2", methods=["GET", "POST"])
@login_required
def registerstu2():
    if request.method == "POST":
        file = request.files['pic']
        f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(f)
        address = "/"+UPLOAD_FOLDER+"/"+file.filename
        dbv.execute("UPDATE profiles SET image = :image WHERE id = :id", image=address, id=session["user_id"])
        return redirect("/registerstu3")
    else:
        return render_template("registerstu2.html")
# Last page for registration where user submits experiences and gets redirected to the homepage to access different pages.


@app.route("/registerstu3", methods=["GET", "POST"])
@login_required
def registerstu3():
    if request.method == "POST":
        if not request.form.get("educational_experience") or not request.form.get("volunteer_experience"):
            return apology("Please provide all inputs", 100)
        dbv.execute("INSERT INTO experience (id) VALUES (:id)", id=session["user_id"])
        dbv.execute("UPDATE experience SET education_experience = :education, volunteer_experience = :volunteer WHERE id = :id",
                    education=request.form.get("educational_experience"), volunteer=request.form.get("volunteer_experience"), id=session["user_id"])
        # Initially, thougt of sending norifications for users after registration but Gmail doesn't allow this app to access it. It should work though.
        # message = "Thank you for registering on our website. We hope you enjoy all the features and remember: KEEP CALM AND VOUNTEER!"
        # sender_address = dbv.execute("SELECT email FROM profiles WHERE id = :id", id=session["user_id"])
        # # session["user_id"] = rows[0]["id"]
        # server = smtplib.SMTP("smtp.gmail.com", 587)
        # server.starttls()
        # server.login("VolunteerAddis@gmail.com", "###")
        # server.sendmail("VolunteerAddis@gmail.com", sender_address, message)
        return redirect("/")
    else:
        return render_template("registerstu3.html")
# If user is a charity/ organization, first form for registration including charity details, location, username and password.


@app.route("/registerorg", methods=["GET", "POST"])
def registerorg():
    if request.method == "POST":
        username = request.form.get("name")
        password = request.form.get("password")
        hash = generate_password_hash(password)
        match = dbc.execute('SELECT * FROM profiles WHERE username = :username', username=username)
        if match:
            return apology("Username is already taken", 505)
        ID = dbc.execute("INSERT INTO profiles (username, hash, category, description, link, latitude, longitude) VALUES (:username, :hash, :category, :description, :link, :lat, :long)", username=username,
                         hash=hash, category=request.form.get("category"), description=request.form.get("description"), link=request.form.get("link"), lat=request.form.get("lat"), long=request.form.get("long"))
        session["org_id"] = ID
        return redirect("/registerorg2")
    else:
        return render_template("registerorg.html")
# Last page of registration for charities to include the charity logo or picture.


@app.route("/registerorg2", methods=["GET", "POST"])
@login_org_required
def registerorg2():
    if request.method == "POST":
        file = request.files['pic']
        f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(f)
        address = "/"+UPLOAD_FOLDER+"/"+file.filename
        dbc.execute("UPDATE profiles SET image = :image WHERE id = :id", image=address, id=session["org_id"])
        # message = "Thank you for registering on our website. We hope you enjoy all the features and remember: KEEP CALM AND VOUNTEER!"
        # sender_address = dbc.execute("SELECT email FROM profiles WHERE id = :id", id=session["org_id"])
        # server = smtplib.SMTP("smtp.gmail.com", 587)
        # server.starttls()
        # server.login("VolunteerAddis@gmail.com", "###")
        # server.sendmail("VolunteerAddis@gmail.com", sender_address, message)
        return redirect("/org")
    else:
        return render_template("registerorg2.html")
# Search page for volunteers to search charities based on name, category submitted by the organization and location.


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        if not request.form.get("search"):
            return apology("Please provide your search criteria", 250)
        elif request.form.get("search") == "name":
            if not request.form.get("Name"):
                return apology("Please provide the name of the organization", 250)
            result = dbc.execute("SELECT * FROM profiles WHERE username = :name", name=request.form.get("Name"))
        elif request.form.get("search") == "category":
            if not request.form.get("Category"):
                return apology("Please provide the cateogry name", 250)
            result = dbc.execute("SELECT * FROM profiles WHERE category = :category", category=request.form.get("Category"))
        elif request.form.get("search") == "distance":
            if not request.form.get("Distance") or int(request.form.get("Distance")) < 0:
                return apology("Please provide correct distance", 250)
            R = 6373
            result = {}
            row1 = dbv.execute("SELECT location_lat, location_long FROM profiles WHERE id = :id", id=session["user_id"])
            lat1=row1[0]
            lon1=row1[1]
            row2 = dbc.execute("SELECT latitude, longitude FROM profiles")
            for element in row2:
                lat2 = element["latitude"]
                lon2 = element["longitude"]
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                distance = R * c
                if distance <= request.form.get("Distnance"):
                    result += element
        return render_template("searchresults.html", result=result)
    else:
        return render_template("search.html")


# a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
# c = 2 * atan2(sqrt(a), sqrt(1 - a))

# distance = R * c
# Profile page for volunteers that they can update experience as well as picture on.


@app.route("/studentprofile", methods=["GET", "POST"])
@login_required
def studentprofile():
    personal = dbv.execute("SELECT * FROM profiles WHERE id = :id", id=session["user_id"])
    name = personal[0]["name"]
    email = personal[0]["email"]
    image = personal[0]["image"]
    experiences = dbv.execute("SELECT * FROM experience WHERE id = :id", id=session["user_id"])
    return render_template("studentprofile.html", name=name, email=email, image=image, experiences=experiences)

# Profile page for organization showing details from database that details were stored in


@app.route("/orgprofile", methods=["GET", "POST"])
@login_org_required
def orgprofile():
    charity = dbc.execute("SELECT * FROM profiles WHERE id = :id", id=session["org_id"])
    name = charity[0]["username"]
    image = charity[0]["image"]
    link = charity[0]["link"]
    description = charity[0]["description"]
    category = charity[0]["category"]
    return render_template("orgprofile.html", name=name, image=image, link=link, description=description, category=category)

# Page for charities to add the volunteer times of volunteers which will be displayed on volunteers' history


@app.route("/orgadd", methods=["GET", "POST"])
@login_org_required
def orgadd():
    if request.method == "POST":
        if not request.form.get("time_worked") or not request.form.get("name"):
            return apology("Please input in all required fields")
        user_id = dbv.execute("SELECT * FROM profiles WHERE name = :username", username=request.form.get("name"))
        if not user_id:
            return apology("Sorry, there is noone in our database with such name")
        orgname = dbc.execute("SELECT * FROM profiles WHERE id = :id", id=session["org_id"])
        dbv.execute("INSERT INTO volunteer (id, organization, time_worked) VALUES(:volunteer_id, :organization, :time_worked)",
                    volunteer_id=user_id[0]["id"], organization=orgname[0]["username"], time_worked=request.form.get("time_worked"))
        return redirect("/orgadd")
    else:
        return render_template("orgadd.html")

# History page to check how much the volunteer worked and even check the details by writing down the name of the organization


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    if request.method == "POST":
        if not request.form.get("name"):
            return apology("Please input in all required fields")
        history = dbv.execute("SELECT time_worked, time_submitted FROM volunteer WHERE id = :user_id AND organization = :organization",
                              user_id=session["user_id"], organization=request.form.get("name"))
        return render_template("historydetail.html", history=history, organization=request.form.get("name"))
    else:
        history = dbv.execute(
            "SELECT organization, SUM(time_worked) AS time_worked FROM volunteer WHERE id = :user_id GROUP BY organization", user_id=session["user_id"])
        return render_template("history.html", history=history)

# Stories page accessible for all to encourage more people to volunteer by posting stories.


@app.route("/stories")
def stories():
    return render_template("stories.html")

# If user forgot password, a user can create a new one after verification through email (but Gmail security problems). Hence, useless page now.


@app.route("/passforgot", methods=["GET", "POST"])
def passforgot():
    if request.method == "POST":
        if not request.form.get("type") or not request.form.get("username"):
            return apology("Please fill out the full form", 300)
        if request.form.get("type") == "volunteer":
            sender_address = dbv.execute("SELECT email FROM profiles WHERE username = :username",
                                         username=request.form.get("username"))
        elif request.form.get("type") == "organization":
            sender_address = dbc.execute("SELECT email FROM profiles WHERE username = :username",
                                         username=request.form.get("username"))
        # message = "The passcode is VoluntAddis. Go back to our webpage and input the given code"
        # server = smtplib.SMTP("smtp.gmail.com", 587)
        # server.starttls()
        # server.login("VolunteerAddis@gmail.com", "###")
        # server.sendmail("VolunteerAddis@gmail.com", sender_address, message)
        return redirect("/passchange")
    else:
        return render_template("passforgot.html")

# Password change page after being redirected from password forgot allowing user to change their password after inputting the passcode


@app.route("/passchange", methods=["GET", "POST"])
def passwordchange():
    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation") or not request.form.get("type"):
            return apology("Please input in all required fields")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords don't match")
        elif request.form.get("passcode") != "VoluntAddis":
            return apology("Passcode is incorrect")
        if request.form.get("type") == "volunteer":
            dbv.execute("UPDATE profiles SET hash = :hash WHERE username = :username", hash=generate_password_hash(
                request.form.get("password")), username=request.form.get("username"))
        if request.form.get("type") == "organization":
            dbc.execute("UPDATE profiles SET hash = :hash WHERE username = :username", hash=generate_password_hash(
                request.form.get("password")), username=request.form.get("username"))
        return redirect("/login")
    else:
        return render_template("passchange.html")


# Feedback form that was supposed to send email to VolunteerAddis but again Gmail problems so was not able to do so.

@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        message = request.form.get("feedback")
        if not message:
            return apology("Please provide your feedback", 100)
        # server = smtplib.SMTP("smtp.gmail.com", 587)
        # server.starttls()
        # server.login("VolunteerAddis@gmail.com", "###")
        # server.sendmail("VolunteerAddis@gmail.com", "VolunteerAddis@gmail.com", message)
        return redirect("/")
    else:
        return render_template("feedback.html")

# Login page from Finance PSet except database and criteria name changes


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if request.form['submit_button'] == 'Forgot Password':
            return redirect('/passforgot')
        if not request.form.get("username"):
            return apology("must provide username", 403)
        if not request.form.get("password"):
            return apology("must provide password", 403)
        if request.form.get("type") == "volunteer":
            user = dbv.execute("SELECT * FROM profiles WHERE username = :username", username=request.form.get("username"))
            if len(user) != 1 or not check_password_hash(user[0]["hash"], request.form.get("password")):
                return apology("invalid username and/or password", 403)
            session["user_id"] = user[0]["id"]
            return redirect("/")
        else:
            user = dbc.execute("SELECT * FROM profiles WHERE username = :username", username=request.form.get("username"))
            if len(user) != 1 or not check_password_hash(user[0]["hash"], request.form.get("password")):
                return apology("invalid username and/or password", 403)
            session["org_id"] = user[0]["id"]
            return redirect("/org")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# Logout page from Finance


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


# https://medium.com/@sightengine_/image-upload-and-moderation-with-python-and-flask-e7585f43828a - image upload and management


from flask import Flask, render_template, flash, redirect, session, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///user"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config['SECRET_KEY'] = "abcdef"

connect_db(app)
db.create_all()

@app.route("/")
def home():
    """Home page"""
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def registration():
    """Register a new user"""

    if "username" not in session:
        form = RegisterForm()

        if form.validate_on_submit():
            first_name = form.first_name.data
            last_name = form.last_name.data
            username = form.username.data
            password = form.password.data
            email = form.email.data

            new_user = User.register(first_name, last_name, username, password, email)

            db.session.add(new_user)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("New user can not be created")
                return redirect("/register")

            session["username"] = new_user.username

            flash("New user created")
            return redirect(f"/users/{new_user.username}")
        else:
            return render_template("register.html", form=form)
    else:
        username = session["username"]
        return redirect(f"/users/{username}")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login an existing user"""

    if "username" not in session:
        form = LoginForm()

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            user = User.authenticate(username, password)

            if user:
                session["username"] = username
                return redirect(f"/users/{username}")
            else:
                flash("Incorrect username/password. Please try again.")
        
        return render_template("login.html", form=form)
    else:
        username = session["username"]
        return redirect(f"/users/{username}")

@app.route("/users/<username>")
def secret(username):
    """Access user html only if user is logged in"""

    if "username" in session:
        user = User.query.filter_by(username=username).first()
        feedbacks = Feedback.query.all()
        return render_template("secret.html", user=user, feedbacks=feedbacks)
    else:
        flash("Please login")
        redirect("/login")
        
    # try:
    #     session["username"]
    #     return render_template("secret.html")
    # except KeyError:
    #     flash("Please login")
    #     redirect("/login")

@app.route("/logout")
def logout():
    """Log out from username"""
    try:
        session.pop("username")
        flash("User logged out")
    except KeyError:
        flash("No user to logout")

    return redirect("/login")

@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    """Add a new feedback for an existing user"""

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        fb = Feedback(title=title, content=content, username=username)

        db.session.add(fb)
        db.session.commit()
        return redirect(f"/users/{username}")

    return render_template("new_feedback.html", form=form)

@app.route("/feedback/<feedback_id>/update", methods=["GET", "POST"])
def view_feedback(feedback_id):
    """Edit an existing feedback"""

    fb = Feedback.query.get_or_404(feedback_id)
    form = FeedbackForm(obj=fb)

    if form.validate_on_submit() and session["username"] == fb.username:
        fb.title = form.title.data
        fb.content = form.content.data

        db.session.add(fb)
        db.session.commit()
        return redirect(f"/users/{session['username']}")

    return render_template("feedback.html", form=form, feedback=fb)

@app.route("/feedback/<feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete an existing feedback"""

    fb = Feedback.query.get_or_404(feedback_id)

    if session["username"] == fb.username:
        db.session.delete(fb)
        db.session.commit()
    else:
        flash("You do not access to delete this")

    return redirect(f"/users/{session['username']}")

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """Delete an existing user and associated feedback"""

    user = User.query.get_or_404(username)

    if session["username"] == username:
        # Delete all feedback from database by logged in user
        feedbacks = user.feedbacks
        for fb in feedbacks:
            db.session.delete(fb)

        # Delete logged in user
        db.session.delete(user)
        db.session.commit()

        session.pop("username")
    else:
        flash("You do not access to delete this")

    return redirect("/login")

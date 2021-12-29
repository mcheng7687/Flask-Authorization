from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    __tablename__ = "personal"

    username = db.Column(db.String(20), 
                        primary_key=True)
    password = db.Column(db.String(),
                        nullable = False)
    email = db.Column(db.String(50),
                        nullable = False,
                        unique = True)
    first_name = db.Column(db.String(30),
                        nullable = False)
    last_name = db.Column(db.String(30),
                        nullable = False)

    def __repr__(self):
        return f"<User obj {self.username}>"

    @classmethod
    def register(cls, first, last, username, pwd, email):
        """Register a new user. Verify if new user is possible."""
        hashed = bcrypt.generate_password_hash(pwd)

        hashed_utf8 = hashed.decode("utf8")

        return cls(first_name = first, last_name = last, username = username, password = hashed_utf8, email = email)


    @classmethod
    def authenticate(cls, username, pwd):
        """Authenticate given username and password from database."""
        user = User.query.filter_by(username=username).first()

        if (user and bcrypt.check_password_hash(user.password, pwd)):
            return user
        else:
            return False

class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer,
                primary_key = True,
                autoincrement = True)
    title = db.Column(db.String(100),
                nullable = False)
    content = db.Column(db.Text,
                nullable = False)
    username = db.Column(db.String(20),
                db.ForeignKey('personal.username'))
    user = db.relationship('User',
                backref = 'feedbacks')

    def __repr__(self):
        return f"<Feedback obj title:{self.title} user:{self.username}>"
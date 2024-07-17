from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """User model"""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png"
    )

    netflix = db.Column(
        db.Boolean
    )

    prime_video = db.Column(
        db.Boolean
    )

    disney_plus = db.Column(
        db.Boolean
    )

    hbo_max = db.Column(
        db.Boolean
    )

    hulu = db.Column(
        db.Boolean
    )

    peacock = db.Column(
        db.Boolean
    )

    paramount_plus = db.Column(
        db.Boolean
    )

    starz = db.Column(
        db.Boolean
    )

    showtime = db.Column(
        db.Boolean
    )

    apple_tv = db.Column(
        db.Boolean
    )


    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"
    
    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    
class Movie(db.Model):
    """Table for each movie"""

    __tablename__ = 'movies'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False
    )

    description = db.Column(
        db.Text,
        default="Movie description here",
        nullable=False
    )

    rating = db.Column(
        db.Text,
        default="Rating goes here",
        nullable=False
    )

    image_url = db.Column(
        db.Text,
        default="Image URL",
        nullable=False
    )

    year = db.Column(
        db.Integer
    )

    runtime = db.Column(
        db.Integer
    )

    genre = db.Column(
        db.Text
    )

class Service(db.Model):
    """The table for each subscription service. Hulu, Netflix, etc."""

    __tablename__ = 'services'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False
    )

class Subscription(db.Model):
    """Subscription table, connects the ID of the movie and streaming service ID"""

    __tablename__ = 'subscriptions'

    movie_id = db.Column(
        db.Integer,
        db.ForeignKey('movies.id', ondelete="CASCADE"),
        primary_key=True
    )

    service_id = db.Column(
        db.Integer,
        db.ForeignKey('services.id', ondelete="CASCADE"),
        primary_key=True
    )

class User_Likes_Movie(db.Model):
    """Table for user to put on watch list """

    __tablename__ = 'user_likes_movies'

    user_liking_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True
    )

    liked_movie_id = db.Column(
        db.Integer,
        db.ForeignKey('movies.id', ondelete="cascade"),
        primary_key=True
    )

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """
    with app.app_context():
        db.app = app
        db.init_app(app)
        db.create_all()
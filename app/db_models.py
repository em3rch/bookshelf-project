from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin
from app.extensions import db, login_manager


# UserMixin is used for predefining 4 methods necessary for Flask-Login:
# is_authenticated - has the user log in to his account.
# is_active - is user's account active? (Not deleted).
# is_anonymous - is the user an anonymous guest?
# get_id() - how to obtain user's unique ID in a text format.


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        nullable=False
    )

    books = db.relationship(
        "Book",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)





class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Fetched from Google Books (or entered manually)
    google_id = db.Column(db.String(100)) # Google Books volume id, nullable for manual entries
    title = db.Column(db.String(300), nullable=False)
    author = db.Column(db.String(200))
    year = db.Column(db.Integer)
    genres = db.Column(db.String(300))
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(500)) 
    cover_image = db.Column(db.String(512))

    # User fields
    status = db.Column(db.String(20), nullable=False, default="wanted") # Can be 1 from the following: wanted | reading | read
    notes = db.Column(db.Text)
    added_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
    )


    BOOK_STATUSES = ("wanted", "reading", "read")



    ALLOWED_COVER_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "webp"
    }


@login_manager.user_loader # Get ID from client browser's cookies and look for a User attached to this ID in User model.
def load_user(user_id):
    return User.query.get(int(user_id)) # .get() func accepts PrimaryKey argument



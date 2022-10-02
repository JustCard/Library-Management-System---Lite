from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(92), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    isAdmin = db.Column(db.Boolean, index=True, unique=False, default=False)
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    author = db.Column(db.String(140))
    qty = db.Column(db.Integer, default=1)
    img = db.Column(db.String(460), default="https://i.imgur.com/S2P76mn.png")

    def __repr__(self):
        return '<Books {}>'.format(self.title)

class Borrowed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow().date())
    status = db.Column(db.Boolean, index=True, unique=False, default=True)

    def __repr__(self):
        return '<Books {}>'.format(self.id)

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(140))

    def __repr__(self):
        return '<Books {}>'.format(self.id)



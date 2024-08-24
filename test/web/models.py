from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

    drivers_post = db.relationship('Driverspost', backref='user', lazy=True)
    profile = db.relationship('Profile', backref='user', lazy=True)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(150))
    gender = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(15), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Driverspost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dateandTime = db.Column(db.String(10), nullable=False)
    pickup = db.Column(db.String(100), nullable=False)
    dropoff = db.Column(db.String(100), nullable=False)
    carplate = db.Column(db.String(100), nullable=False)
    carmodel = db.Column(db.String(100), nullable=False)
    totalperson = db.Column(db.Integer, nullable=False)
    fees = db.Column(db.String(100), nullable=False)
    duitnowid = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(100), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)




# class Note(db.Model):
#     id=db.Column(db.Integer,primary_key=True)
#     data=db.Column(db.String(10000))
#     date=db.Column(db.DateTime(timezone=True),default=func.now())
#     user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
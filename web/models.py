from . import db
from flask_login import UserMixin



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

    drivers_post = db.relationship('Driverspost', backref='user', lazy=True)
    profile = db.relationship('Profile', backref='user', lazy=True)
    passenger_matches = db.relationship('PassengerMatch', foreign_keys='PassengerMatch.passenger_id', backref='passenger_match', lazy=True)

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
    status = db.Column(db.String(20), nullable=False, default='ongoing')
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    passenger_matches = db.relationship('PassengerMatch', foreign_keys='PassengerMatch.driver_id', backref='driver_post', lazy=True)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(150))
    gender = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    profile_pic = db.Column(db.String(200), default="default.jpg")  # Make sure this column is present
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    birthyear = db.Column(db.String(15), nullable=False)


class PassengerMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driverspost.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='ongoing')
    
    passenger = db.relationship('User', foreign_keys=[passenger_id], backref='matches_as_passenger')
    driver = db.relationship('Driverspost', foreign_keys=[driver_id], backref='matches_as_driver')
from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)  # Add this line

    drivers_post = db.relationship('Rides', backref='user', lazy=True)
    profile = db.relationship('Profile', backref='user', lazy=True)
    passenger_matches = db.relationship('PassengerMatch', foreign_keys='PassengerMatch.passenger_id', backref='passenger_match', lazy=True)

class Rides(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dateandTime = db.Column(db.String(50), nullable=False)
    start_location = db.Column(db.String(100), nullable=False)
    start_location_lat = db.Column(db.Float, nullable=True)  # Nullable
    start_location_lng = db.Column(db.Float, nullable=True)  # Nullable
    end_location = db.Column(db.String(100), nullable=False)
    end_location_lat = db.Column(db.Float, nullable=True)  # Nullable
    end_location_lng = db.Column(db.Float, nullable=True)  # Nullable
    carplate = db.Column(db.String(20), nullable=False)
    carmodel = db.Column(db.String(50), nullable=False)
    totalperson = db.Column(db.Integer, nullable=False)
    fees = db.Column(db.String(50), nullable=False)
    duitnowid = db.Column(db.String(50), nullable=True)  # Nullable
    message = db.Column(db.Text, nullable=True)  # Nullable
    status = db.Column(db.String(50), nullable=False,default='pending') #approved
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    passenger_matches = db.relationship('PassengerMatch', foreign_keys='PassengerMatch.driver_id', backref='driver_post', lazy=True)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(150))
    gender = db.Column(db.String(100), nullable=False)
    birthyear=db.Column(db.String(15), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    birthyear = db.Column(db.String(15), nullable=False)
    profile_pic = db.Column(db.String(200), default="default.jpg")  
    is_approved = db.Column(db.Boolean, default=False)  # Added for moderation
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    birthyear = db.Column(db.String(15), nullable=False)


class PassengerMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('rides.id'), nullable=False)
    payment_proof_id = db.Column(db.Integer, db.ForeignKey('payment_proof.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='APPROVING')
    
    passenger = db.relationship('User', foreign_keys=[passenger_id], backref='matches_as_passenger')
    driver = db.relationship('Rides', foreign_keys=[driver_id], backref='matches_as_driver')
    # Relationship with PaymentProof
    payment_proof = db.relationship('PaymentProof', backref='matches', lazy=True)

class PaymentProof(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('profile.user_id'), nullable=False)
    user = db.relationship('Profile', backref='payment_proofs', lazy=True)
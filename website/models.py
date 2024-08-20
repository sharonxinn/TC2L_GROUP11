from . import db
from flask_login import UserMixin
from sqlalchemy import func

class Note(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    data=db.Column(db.String(10000))
    date=db.Column(db.DateTime(timezone=True),default=func.now())
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(150),unique=True)
    password=db.Column(db.String(150))
    first_name=db.Column(db.String(150))
    
   
class Carpool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(100), nullable=False)
    dateandTime = db.Column(db.String(10), nullable=False)
    pickup = db.Column(db.String(100), nullable=False)
    dropoff = db.Column(db.String(100), nullable=False)
    totalperson = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(100), nullable=False)


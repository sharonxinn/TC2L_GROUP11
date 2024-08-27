from . import db
from flask_login import UserMixin
from sqlalchemy import func


class Note(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    data=db.Column(db.String(10000))
    date=db.Column(db.DateTime(timezone=True),default=func.now())
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(150))
    gender = db.Column(db.String(50))
    contact = db.Column(db.String(150))
    profile_pic = db.Column(db.String(150), nullable=True)  # Add this line
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))




    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email}"



    
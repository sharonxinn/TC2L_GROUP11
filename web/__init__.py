from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import urllib.request
import os

db = SQLAlchemy()
login_manager = LoginManager()

UPLOAD_FOLDER='static/uploads/'
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carpooling.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH']=16*1024*1024

    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    from .models import User, Driverspost, Profile, PassengerMatch

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app

from flask import Flask,redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,logout_user,login_required
from flask_admin import Admin,expose,BaseView
from flask_admin.contrib.sqla import ModelView
import os

db = SQLAlchemy()
login_manager = LoginManager()

UPLOAD_FOLDER='static/uploads/'
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carpooling.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH']=16*1024*1024

    # Ensure the directory exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.home'

    from .models import User, Driverspost, Profile, PassengerMatch

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)
    # Admin Logout View
    class AdminLogoutView(BaseView):
        @expose('/')
        @login_required
        def index(self):
            logout_user()
            flash("Logged Out Successfully!", category='success')
            return redirect(url_for('main.home'))

    # Setup Flask-Admin
    admin = Admin(app)
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Driverspost, db.session))
    admin.add_view(ModelView(Profile, db.session))
    admin.add_view(ModelView(PassengerMatch, db.session))
    admin.add_view(AdminLogoutView(name="Log Out",endpoint="logout"))


    return app




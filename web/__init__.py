from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_mail import Mail
from werkzeug.security import generate_password_hash
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carpooling.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'mmucarpooling@gmail.com'
    app.config['MAIL_PASSWORD'] = 'opzefykwjmvybkep'
    app.config['MAIL_DEFAULT_SENDER'] = 'mmucarpooling@gmail.com'
    
    # Set up upload folder
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.home'
    mail.init_app(app)

    from .models import User, Rides, Profile, PassengerMatch


    # Define the user loader function
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User  # Import here to avoid circular imports
        return User.query.get(int(user_id))

    # Initialize Flask-Admin
    from .adminviews import AdminIndex, AdminModelView, ProfileModelView, AdminLogoutView,RiderPostModelView
    admin = Admin(app, template_mode='bootstrap4', index_view=AdminIndex())
    
    # Add views for admin
    from .models import User, Profile,Rides # Import here to avoid circular imports
    admin.add_view(AdminModelView(User, db.session))
    admin.add_view(ProfileModelView(Profile, db.session))
    admin.add_view(RiderPostModelView(Rides, db.session))
    admin.add_view(AdminLogoutView(name="Log Out", endpoint="logout"))

    # Register blueprints
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Create database tables and add admin user if not exists
    with app.app_context():
        db.create_all()
        add_admin_to_db(app)

    return app

def add_admin_to_db(app):
    with app.app_context():
        from .models import User  # Import here to avoid circular imports
        email = "admin@gmail.com"
        password = "admin123"

        admin_in_db = User.query.filter_by(email=email).first()

        if not admin_in_db:
            admin_user = User(
                email=email,
                password=generate_password_hash(password, method="scrypt"),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin successfully added!")

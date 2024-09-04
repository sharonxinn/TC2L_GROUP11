from flask import Blueprint, render_template, request, flash, redirect, url_for,Flask,session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Driverspost, Profile,PassengerMatch
from . import db
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
bp = Blueprint('main', __name__)
app.config['UPLOAD_FOLDER']='/web/static/uploads/'

#set up login page
@bp.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        entered_captcha = request.form.get('text')
        generated_captcha = request.form.get('captcha_code')

        user=User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully',category='success')
                login_user(user,remember=True)
                return redirect(url_for('main.base'))
            else:
                flash('Incorrect password,try again',category='error')

        if request.form.get("email")=="admin@gmail.com" and request.form.get("password")=="admin1234":
            session['logged in']=True
            return redirect("/admin")
        
        elif entered_captcha is None or entered_captcha.lower() != generated_captcha:
            flash('Verification Code Error!', category='error')

        else:
            if user:
                if check_password_hash(user.password, password):
                    flash('Logged in successfully',category='success')
                    login_user(user,remember=True)
                    return redirect(url_for('main.chooseid'))
                else:
                    flash('Incorrect password,try again',category='error')
            else:
                flash('Email does not exist.',category='error')
    
    return render_template("login.html",user=current_user)

#set up home page
@bp.route('/')
def home():
    return render_template('home.html',user=current_user)


def file_is_valid(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'png', 'jpeg'}



#set up sidebar page

@bp.route('/sidebar')
def sidebar():
    return render_template('sidebar.html',user=current_user)

@bp.route('/base')
def base():
    return render_template('base.html',user=current_user,profile=profile)


#set up profile page
def file_is_valid(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'png', 'jpeg'}


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        fullName = request.form['fullName']
        gender = request.form['gender']
        birthyear = request.form['birthyear']
        contact = request.form['contact']
        birthyear = request.form['birthyear']
        file = request.files.get('file')

        # Handling file upload (if any)
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            upload_path = os.path.join('web', 'static', 'uploads')

            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            
            file_path = os.path.join(upload_path, filename)
            print("Saving file to:", file_path)  
            
            try:
                file.save(file_path)
            except Exception as e:
                flash(f"An error occurred while saving the file: {e}", category="error")
                return redirect(url_for('main.profile'))

            # Create the image URL
            image_url = f'/static/uploads/{filename}'

        new_Profile = Profile(
            fullName=fullName,
            gender=gender,
            contact=contact,
            birthyear=birthyear,
            user_id=current_user.id,
            profile_pic=image_url  # Assigning the image_url to profile_pic
        )

        db.session.add(new_Profile)
        db.session.commit()

        return redirect(url_for('main.chooseid'))

    return render_template('profile.html')

#set up chooseid page
@bp.route('/chooseid', methods=['GET', 'POST'])
@login_required
def chooseid():
    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'passenger':
            return redirect(url_for('main.base'))
        elif role == 'driver':
            return redirect(url_for('main.driver_post'))
    return render_template('chooseid.html')

#set up google map page
@bp.route('/googlemap')
@login_required
def googlemap():
    return render_template('googlemap.html', user=current_user)

#set up logout page
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

#set up sign up page
@bp.route('/signup',methods=['GET','POST'])
def sign_up():
    if request.method=='POST':
        email=request.form.get('email')
        password1=request.form.get('password1')
        password2=request.form.get('password2')
        entered_captcha = request.form.get('text')
        generated_captcha = request.form.get('captcha_code')

        user=User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists',category='error')
        elif len(email)<4:
            flash('Email must be greater than 3 characters.',category='error')
        # elif len(first_name)<2:
        #     flash('First Name must be greater than 1 characters.',category='error')
        elif password1 != password2:
            flash('Password does not match.',category='error')
        elif len(password1)<7:
            flash('Password must be greater than 6 characters.',category='error')
        elif entered_captcha is None or entered_captcha.lower() != generated_captcha:
            flash('Verification Code Error!', category='error')
        else:
            new_user=User(email=email,password=generate_password_hash(password1,method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            user = User.query.filter_by(email=email).first()

            if user:  # Check if user is found
                login_user(user, remember=True)
                flash('Account created successfully!', category='success')
                return redirect(url_for('main.profile'))
            else:
                flash('Error during user creation. Please try again.', category='error')

    return render_template("signup.html",user=current_user)


#set up driver post page
@bp.route('/driver_post', methods=['GET', 'POST'])
@login_required
def driver_post():
    if request.method == 'POST':
        dateandTime = request.form['dateandTime']
        pickup = request.form['pickup']
        dropoff = request.form['dropoff']
        carplate = request.form['carplate']
        carmodel = request.form['carmodel']
        totalperson = request.form['totalperson']
        fees = request.form['fees']
        duitnowid = request.form['duitnowid']
        message = request.form['message']
        status = 'in_progress'

        new_Driverspost = Driverspost(
            dateandTime=dateandTime,
            pickup=pickup,
            dropoff=dropoff,
            carplate=carplate,
            carmodel=carmodel,
            totalperson=totalperson,
            fees=fees,
            duitnowid=duitnowid,
            message=message,
            status= status,
            user_id=current_user.id
        )

        db.session.add(new_Driverspost)
        db.session.commit()

        return redirect(url_for('main.base',driver_id=current_user.id))

    return render_template('driver_post.html')

#set up driver list page
@bp.route('/drivers_list')
@login_required
def drivers_list():
    drivers = Driverspost.query.filter_by(status='in_progress')
    profiles = Profile.query.all()
    profile_dict = {profile.user_id: profile for profile in profiles}


    return render_template('drivers_list.html', drivers=drivers, profile_dict=profile_dict,profile=profile)



@bp.route('/profile_list')
@login_required
def profile_list():
    profiles = Profile.query.all()

    return render_template('profile_list.html', profiles=profiles)
 

#     return render_template('user_list.html', users=users)

# @bp.route('/profile_list')
# @login_required
# def profile_list():
#     profiles = Profile.query.all()

#     return render_template('profile_list.html', profiles=profiles)

#set up match_passsenger page
@bp.route('/match_passenger/<int:driver_id>')
@login_required
def match_passenger(driver_id):
    driver = Driverspost.query.get_or_404(driver_id)
    profiles = Profile.query.all()
    profile_dict = {profile.user_id: profile for profile in profiles}
    passengers = PassengerMatch.query.filter_by(driver_id=driver_id, status='in_progress').all()  
    return render_template('match_passenger.html', driver=driver, passengers=passengers, profile_dict=profile_dict)

#set up match driver page
@bp.route('/match_driver/<int:driver_id>')
@login_required
def match_driver(driver_id):
    driver = Driverspost.query.get_or_404(driver_id)
    profiles = Profile.query.all()
    profile_dict = {profile.user_id: profile for profile in profiles}
    passengers = PassengerMatch.query.filter_by(driver_id=driver_id, status='in_progress').all() 
    return render_template('match_driver.html', driver=driver, passengers=passengers, profile_dict=profile_dict)

#set up select driver page
@bp.route('/select_driver/<int:driver_id>', methods=['POST'])
@login_required
def select_driver(driver_id):
    selected_driver = Driverspost.query.get_or_404(driver_id)
    
    existing_match = PassengerMatch.query.filter_by(passenger_id=current_user.id, driver_id=driver_id, status="in_progress").first()
    if existing_match:
        flash('You have already selected this driver.', 'info')
        return redirect(url_for('main.drivers_list'))
    
    
    passenger_match = PassengerMatch(passenger_id=current_user.id, driver_id=selected_driver.id)
    db.session.add(passenger_match)
    db.session.commit()
    
    flash('Driver selected successfully.', category='success')
    return redirect(url_for('main.booking_history', driver_id=driver_id))

#set up remove passenger page
@bp.route('/remove_passenger/<int:passenger_id>/<int:driver_id>', methods=['POST'])
@login_required
def remove_passenger(passenger_id, driver_id):
    passenger_match = PassengerMatch.query.filter_by(passenger_id=passenger_id, driver_id=driver_id).first_or_404()
    
    # Allow the passenger, the driver, or an admin to remove the passenger
    driver_post = Driverspost.query.get_or_404(driver_id)
    if (passenger_match.passenger_id == current_user.id or
        driver_post.user_id == current_user.id or
        current_user.has_role('admin')):
        
        db.session.delete(passenger_match)
        db.session.commit()
        flash('Passenger removed successfully', category='success')
        
        # Redirect depending on who performed the removal
        if current_user.id == driver_post.user_id:
            return redirect(url_for('main.match_driver', driver_id=driver_id))
        else:
            return redirect(url_for('main.match_passenger', driver_id=driver_id))
    
    flash('You do not have permission to remove this passenger.', category='error')
    return redirect(url_for('main.match_passenger', driver_id=driver_id))

# define route for changing password
@bp.route('/change_password',methods=['GET','POST'])
def change_password():
    if request.method == "POST":
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')





@bp.route('/complete_match/<int:match_id>', methods=['POST'])
def complete_match(match_id):
    match = PassengerMatch.query.get(match_id)
    if match:
        match.status = 'complete'
        db.session.commit()

        driver_post = match.driver_post
        driver_post.status = ' completed '
        db.session.commit()

    return redirect(url_for('main.booking_history'))

@bp.route('/cancel_match/<int:match_id>', methods=['POST'])
def cancel_match(match_id):
    match = PassengerMatch.query.get(match_id)
    if match:
        match.status = 'canceled'
        db.session.commit()

        driver_post = match.driver_post
        driver_post.status = 'canceled'
        db.session.commit()

    return redirect(url_for('main.booking_history'))




@bp.route('/view_detail_d/<int:match_id>', methods=['GET', 'POST'])
@login_required
def view_detail_d(match_id):
    match = PassengerMatch.query.get_or_404(match_id)
    return redirect(url_for('main.match_passenger', driver_id=match.driver_id))

@bp.route('/view_detail_p/<int:match_id>', methods=['GET', 'POST'])
@login_required
def view_detail_p(match_id):
    match = PassengerMatch.query.get_or_404(match_id)
    return redirect(url_for('main.match_driver', driver_id=match.driver_id))

#set up bookinh history page
@bp.route('/booking_history')
@login_required
def riderpost_history():
    # Get all matches where the current user is a passenger
    passenger_matches = PassengerMatch.query.join(User, PassengerMatch.passenger_id == User.id) \
                                            .join(Driverspost, PassengerMatch.driver_id == Driverspost.id) \
                                            .filter(PassengerMatch.passenger_id == current_user.id) \
                                            .all()

    # Get all drivers posts where the current user is the driver
    driver_posts = Driverspost.query.filter_by(user_id=current_user.id).all()

    profiles = Profile.query.all()
    profile_dict = {profile.user_id: profile for profile in profiles}

    return render_template('booking_history.html', passenger_matches=passenger_matches, driver_posts=driver_posts, profile_dict=profile_dict)


#@bp.route('/dashboard')
#@login_required
#def dashboard():
    # Fetch the user's profile data from the database
    profile = Profile.query.filter_by(user_id=current_user.id).first()

    if profile is None:
        flash("No profile found. Please complete your profile first.", category="error")
        return redirect(url_for('main.profile'))

    return render_template('dashboard.html', profile=profile)



#set up dashboard page
@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if profile is None:
        flash("No profile found. Please complete your profile first.", category="error")
        return redirect(url_for('main.profile'))

    return render_template('dashboard.html', profile=profile)

UPLOAD_FOLDER = '/static/uploads'
def file_is_valid(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'png', 'jpeg'}

#set up update profile page
@bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash("Profile not found.", category="error")
        return redirect(url_for('main.dashboard'))
    profile.fullName = request.form['fullName']
    profile.contact = request.form['contact']
    email = request.form['email']
    if email != current_user.email:
        user = User.query.filter_by(id=current_user.id).first()
        user.email = email
        db.session.commit()

    file = request.files.get('profile_pic')

    # Handling file upload (if any)
    if file and file.filename != '':
        if file_is_valid(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(UPLOAD_FOLDER)

            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            
            file_path = os.path.join(upload_path, filename)
            print("Saving file to:", file_path)  # Debugging: Print file path
            
            try:
                file.save(file_path)
                profile.profile_pic = filename  # Store the filename in the profile object
            except Exception as e:
                flash(f"An error occurred while saving the file: {e}", category="error")
                return redirect(url_for('main.dashboard'))
        else:
            flash("Invalid file type. Only JPG, PNG, and JPEG files are allowed.", category="error")
            return redirect(url_for('main.dashboard'))

    db.session.commit()
    flash("Profile updated successfully!", category="success")
    return redirect(url_for('main.dashboard'))
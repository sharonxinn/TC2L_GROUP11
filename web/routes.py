from flask import Blueprint, render_template, request, flash, redirect, url_for,Flask,session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Rides, Profile,PassengerMatch,PaymentProof
from .form import PaymentForm
from . import db
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import and_
import os

app = Flask(__name__)
bp = Blueprint('main', __name__)
UPLOAD_FOLDER = '/web/static/uploads/'
app.config['UPLOAD_FOLDER']='/web/static/uploads/'
app.config['UPLOAD_PAYMENT']='/web/static/payment/'


@bp.route('/mu')
def test():
    return render_template('test.html',user=current_user)

#set up sign up page
@bp.route('/signup',methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        entered_captcha = request.form.get('captcha_input')
        generated_captcha = request.form.get('captcha_code')

        if entered_captcha is None or entered_captcha.lower() != generated_captcha:
            flash('Verification Code Error!', category='error')
            return redirect(url_for('main.signup'))

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists', category='error')

        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')

        elif password1 != password2:
            flash('Passwords do not match.', category='error')

        elif len(password1) < 7:
            flash('Password must be greater than 6 characters.', category='error')

        else:
            new_user = User(email=email, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()

            user = User.query.filter_by(email=email).first()

            if user:
                login_user(user, remember=True)
                flash('Account created successfully!', category='success')
                return redirect(url_for('main.profile'))
            else:
                flash('Error during user creation. Please try again.', category='error')

    return render_template("signup.html", user=current_user)


#set up login page
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        entered_captcha = request.form.get('captcha_input')
        generated_captcha = request.form.get('captcha_code')

        if entered_captcha is None or entered_captcha.lower() != generated_captcha:
            flash('Verification Code Error!', category='error')
            return redirect(url_for('main.login'))

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            flash('Logged in successfully', category='success')
            login_user(user, remember=True)
            if user.is_admin:
                return redirect(url_for('admin.index'))
            else:
                return redirect(url_for('main.chooseid'))
        elif user:
            flash('Incorrect password. Please try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@bp.route('/forgotpassword')
def forgotpassword():
    return render_template('forgotpassword.html',user=current_user)

#set up logout page
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

#set up home page
@bp.route('/')
def home():
    return render_template('home.html',user=current_user)

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

#set up sidebar page
@bp.route('/sidebar')
def sidebar():
    return render_template('sidebar.html',user=current_user)

#set up base page
@bp.route('/base')
def base():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    return render_template('base.html', user=current_user, profile=profile)

#set up dashboard page
@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    profile = Profile.query.filter_by(user_id=current_user.id,status="approved").first()
    if profile is None:
        flash("No profile found. Please complete your profile first.", category="error")
        return redirect(url_for('main.profile'))

    return render_template('dashboard.html', profile=profile)

#set up update profile page
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@bp.route('/editprofile', methods=['GET', 'POST'])
@login_required
def editprofile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'GET':
        # Render the profile edit page
        if not profile:
            flash("Profile not found.", category="error")
            return redirect(url_for('main.dashboard'))
        
        return render_template('editprofile.html', profile=profile)

    elif request.method == 'POST':
        # Handle form data with appropriate checks
        fullName = request.form.get('fullName')
        contact = request.form.get('contact')
        email = request.form.get('email')

        # Check if the fields exist in the form
        if not fullName or not contact or not email:
            flash("Please fill in all required fields.", category="error")
            return redirect(url_for('main.editprofile'))

        profile.fullName = fullName
        profile.contact = contact

        if email != current_user.email:
            current_user.email = email
            db.session.commit()

        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_path = os.path.join('web', 'static', 'uploads')

                # Ensure upload directory exists
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)

                file_path = os.path.join(upload_path, filename)
                file.save(file_path)

                # Store relative path or URL to access it easily
                profile.profile_pic = f'static/uploads/{filename}'

        db.session.commit()
        flash("Profile updated successfully!", category="success")
        return redirect(url_for('main.dashboard'))


# define route for changing password
@bp.route('/change_password',methods=['GET','POST'])
@login_required
def change_password():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if request.method == "POST":
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')
        if old_password == new_password:
            flash("Old password and new password are the same.", category='error')
        elif new_password != confirm_new_password:
            flash("New password don't match.",category="error")
        elif check_password_hash(current_user.password, old_password):
            current_user.password = generate_password_hash(new_password,method='scrypt')
            db.session.commit()
            flash('Password successfully changed.',category='success')
            return redirect(url_for('main.editprofile'))
        else:
            db.session.rollback()
            flash("Incorrect old password.",category='error')

    return render_template('change_password.html',user=current_user,profile=profile)


####GOOGLE MAP DATA#######################################################################

#set up driver post page
@bp.route('/driver_post', methods=['GET', 'POST'])
@login_required
def driver_post():
    if request.method == 'POST':
        dateandTime = request.form['dateandTime']
        start_location = request.form['start_location']  # Location name from Google Places
        start_location_lat = request.form.get('start_location_lat', None)
        start_location_lng = request.form.get('start_location_lng', None)
        end_location = request.form['end_location']
        carplate = request.form['carplate']
        carmodel = request.form['carmodel']
        totalperson = request.form['totalperson']
        fees = request.form['fees']
        duitnowid = request.form['duitnowid'] if 'duitnowid' in request.form else None
        message = request.form['message']
        status = 'IN PROGRESS'

        # Convert empty strings to None for latitude and longitude
        start_location_lat = float(start_location_lat) if start_location_lat else None
        start_location_lng = float(start_location_lng) if start_location_lng else None

        new_Rides = Rides(
            dateandTime=dateandTime,
            start_location=start_location,
            start_location_lat=start_location_lat,
            start_location_lng=start_location_lng,
            end_location=end_location,
            carplate=carplate,
            carmodel=carmodel,
            totalperson=totalperson,
            fees=fees,
            duitnowid=duitnowid,
            message=message,
            status=status,
            user_id=current_user.id
        )
        db.session.add(new_Rides)
        db.session.commit()

        return redirect(url_for('main.base'))

    return render_template('driver_post.html')

@bp.route('/findarides')
@login_required
def findarides():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    today = datetime.now()

    # Filter rides within the specified range and time (e.g., today's rides)
    driver_posts = Rides.query.filter(
        and_(
            Rides.dateandTime >= today,  # Only show rides happening from today onwards
            Rides.status == 'IN PROGRESS',  # Only show active rides
            Rides.user_id != current_user.id  # Exclude posts by the current user
        )
        ).all()

    # Prepare a list of filtered drivers' details
    drivers_data = []
    for dp in driver_posts:
        if isinstance(dp.dateandTime, datetime):
            dateandTime_str = dp.dateandTime.strftime('%Y-%m-%d %H:%M:%S')
        else:
            dateandTime_str = dp.dateandTime  # Assuming it's already in the desired format

        drivers_data.append({
            'lat': dp.start_location_lat,
            'lng': dp.start_location_lng,
            'end_location': dp.end_location,
            'dateandTime': dateandTime_str,
            'totalperson': dp.totalperson,
            'fees': dp.fees,
            'message': dp.message,
            'status': dp.status,
            'id': dp.id,  
        })
    start_location_lat = 0
    start_location_lng = 0

    return render_template('findarides.html', drivers_data=drivers_data, start_location_lat=start_location_lat, start_location_lng=start_location_lng, profile=profile)

####DRIVER PASSENGER DATA#######################################################################

#set up driver list
@bp.route('/drivers_list')
@login_required
def drivers_list():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    # Get the nearby driver IDs from the query parameters
    nearby_driver_ids = request.args.get('nearbyDrivers')
    if nearby_driver_ids:
        nearby_driver_ids = [int(driver_id) for driver_id in nearby_driver_ids.split(',')]
        drivers = Rides.query.filter(Rides.id.in_(nearby_driver_ids) ).all()
    else:
        drivers = []
    profiles = Profile.query.all()
    profile_dict = {profile.user_id: profile for profile in profiles}
    return render_template('drivers_list.html', drivers=drivers, profile_dict=profile_dict, profile=profile)

#set up booking history page

@bp.route('/booking_history')
@login_required
def booking_history():
    profile = Profile.query.filter_by(user_id=current_user.id).first()

    # Get all matches where the current user is a passenger
    passenger_matches = PassengerMatch.query.join(User, PassengerMatch.passenger_id == User.id) \
                                            .join(Rides, PassengerMatch.driver_id == Rides.id) \
                                            .filter(PassengerMatch.passenger_id == current_user.id) \
                                            .all()

    # Get all drivers posts where the current user is the driver and join PassengerMatch
    driver_posts = Rides.query.filter_by(user_id=current_user.id).all()

    driver_matches_dict = {}
    for post in driver_posts:
        # Filter matches based on 'APPROVING' or 'IN PROGRESS' status
        matches = PassengerMatch.query.filter(PassengerMatch.driver_id == post.id) \
                                      .filter(PassengerMatch.status.in_(['APPROVING', 'IN PROGRESS'])) \
                                      .all()  
        driver_matches_dict[post.id] = matches

    profiles = Profile.query.all()
    profile_dict = {profile.user_id: profile for profile in profiles}

    return render_template('booking_history.html', 
                           passenger_matches=passenger_matches, 
                           profile_dict=profile_dict, 
                           driver_posts=driver_posts, 
                           profile=profile,
                           driver_matches_dict=driver_matches_dict)

#set up match_passsenger page
@bp.route('/match_passenger/<int:driver_id>')
@login_required
def match_passenger(driver_id):

    profile = Profile.query.filter_by(user_id=current_user.id).first()

    driver = Rides.query.get_or_404(driver_id)
    driver_id=driver_id

    profiles = Profile.query.all()
    profile_dict = {profile.user_id: profile for profile in profiles}

    matches = PassengerMatch.query.filter_by(driver_id=driver_id, status='IN PROGRESS').all()
    matches_approving = PassengerMatch.query.filter_by(driver_id=driver_id, status='APPROVING').all()
    matches_completed = PassengerMatch.query.filter_by(driver_id=driver_id, status='COMPLETED').all()
    matches_confirmed = PassengerMatch.query.filter_by(driver_id=driver_id, status='confirm').all()

    # Debugging: print to check contents
    print(f"Profile dict keys: {profile_dict.keys()}")
    print(f"Driver user ID: {driver.user_id}")

    return render_template(
        'match_passenger.html',
        driver=driver,
        driver_id=driver_id,
        matches=matches,  
        profile_dict=profile_dict,
        profile=profile,
        matches_approving=matches_approving,
        matches_completed=matches_completed,
        matches_confirmed=matches_confirmed
    )

@bp.route('/passenger_matched/<int:driver_id>')
@login_required
def passenger_matched(driver_id):

    profile = Profile.query.filter_by(user_id=current_user.id).first()

    driver = Rides.query.get_or_404(driver_id)

    profiles = Profile.query.all()
    profile_dict = {profile.user_id: profile for profile in profiles}

    matches = PassengerMatch.query.filter_by(driver_id=driver_id, status='IN PROGRESS').all()
    matches_approving = PassengerMatch.query.filter_by(driver_id=driver_id, status='APPROVING').all()
    matches_completed = PassengerMatch.query.filter_by(driver_id=driver_id, status='COMPLETED').all()
    matches_confirmed = PassengerMatch.query.filter_by(driver_id=driver_id, status='confirm').all()

    # Debugging: print to check contents
    print(f"Profile dict keys: {profile_dict.keys()}")
    print(f"Driver user ID: {driver.user_id}")

    return render_template(
        'passenger_matched.html',
        driver=driver,
        driver_id=driver_id,
        matches=matches,  
        profile_dict=profile_dict,
        profile=profile,
        matches_approving=matches_approving,
        matches_completed=matches_completed,
        matches_confirmed=matches_confirmed
    )

@bp.route('/waiting_list/<int:driver_id>')
@login_required
def waiting_list(driver_id):

    profile = Profile.query.filter_by(user_id=current_user.id).first()

    driver = Rides.query.get_or_404(driver_id)

    profiles = Profile.query.all()
    profile_dict = {profile.user_id: profile for profile in profiles}

    matches = PassengerMatch.query.filter_by(driver_id=driver_id, status='IN PROGRESS').all()
    matches_approving = PassengerMatch.query.filter_by(driver_id=driver_id, status='APPROVING').all()
    matches_completed = PassengerMatch.query.filter_by(driver_id=driver_id, status='COMPLETED').all()
    matches_confirmed = PassengerMatch.query.filter_by(driver_id=driver_id, status='confirm').all()

    # Debugging: print to check contents
    print(f"Profile dict keys: {profile_dict.keys()}")
    print(f"Driver user ID: {driver.user_id}")

    return render_template(
        'waiting_list.html',
        driver=driver,
        driver_id=driver_id,
        matches=matches,  
        profile_dict=profile_dict,
        profile=profile,
        matches_approving=matches_approving,
        matches_completed=matches_completed,
        matches_confirmed=matches_confirmed
    )


#set up match driver page
@bp.route('/match_drivers/<int:driver_id>')
@login_required
def match_drivers(driver_id):
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    driver = Rides.query.get_or_404(driver_id)
    profiles = Profile.query.all()
    profile_dict = {profile.user_id: profile for profile in profiles}
    passengers = PassengerMatch.query.filter_by(driver_id=driver_id, status='IN PROGRESS' ).all() 
    passengers_approving = PassengerMatch.query.filter_by(driver_id=driver_id, status='APPROVING' ).all() 
    passengers_completed = PassengerMatch.query.filter_by(driver_id=driver_id, status='COMPLETED' ).all() 
    passengers_confirmed = PassengerMatch.query.filter_by(driver_id=driver_id, status='confirm' ).all() 
    return render_template('match_driver.html', 
                           driver=driver,
                            passengers=passengers, 
                            profile_dict=profile_dict,
                            profile=profile,
                            passengers_approving=passengers_approving,
                            passengers_completed=passengers_completed,
                            passengers_confirmed=passengers_confirmed)

#set up select driver page
@bp.route('/select_driver/<int:driver_id>', methods=['POST'])
@login_required
def select_driver(driver_id):
    selected_driver = Rides.query.get_or_404(driver_id)
    
    # existing_match = PassengerMatch.query.filter_by(passenger_id=current_user.id, driver_id=driver_id).first()
    # if existing_match:
    #     flash('You have already selected this driver.', 'info')
    #     return redirect(url_for('main.drivers_list'))
    
    
    passenger_match = PassengerMatch(passenger_id=current_user.id, driver_id=selected_driver.id)
    db.session.add(passenger_match)
    db.session.commit()
    
    flash('Driver selected successfully.', category='success')
    return redirect(url_for('main.booking_history', driver_id=driver_id))

#set up remove passenger page
@bp.route('/remove_passenger/<int:match_id>', methods=['POST'])
@login_required
def remove_passenger(match_id):
    match = PassengerMatch.query.get(match_id)
    if match:
        match.status = 'REJECTED'
        db.session.commit()

    return redirect(url_for('main.passenger_matched',driver_id=current_user.id))

@bp.route('/approve_passenger/<int:match_id>', methods=['POST'])
@login_required
def approve_passenger(match_id):
    match = PassengerMatch.query.get(match_id)
    if match:
        match.status = 'IN PROGRESS'
        db.session.commit()

    return redirect(url_for('main.passenger_matched',driver_id=current_user.id))

#set up confirm match page
@bp.route('/confirm_match/<int:match_id>', methods=['POST'])
def confirm_match(match_id):
    match = PassengerMatch.query.get(match_id)
    if match:
        match.status = 'confirm'

        # Find the latest payment proof for this passenger
        payment_proof = PaymentProof.query.filter_by(user_id=match.passenger_id).order_by(PaymentProof.id.desc()).first()
        if payment_proof:
            match.payment_proof_id = payment_proof.id

        db.session.commit()

        driver_post = match.driver_post
        driver_post.status = 'confirmed'
        db.session.commit()

        # Redirect to the match_passenger page or another relevant page
        return redirect(url_for('main.upload_payment_proof', match_id=match_id))

    return redirect(url_for('main.booking_history'))

#set up cancel match page
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
@login_required
def cancel_match(match_id):
    matches = PassengerMatch.query.filter_by(driver_id=match_id).all()
    
    if matches:
        for match in matches:
            match.status = 'CANCELED'
        
        driver_post = Rides.query.get_or_404(match_id)
        driver_post.status = 'CANCELED'
        
        db.session.commit()
        flash('Match and driver post have been canceled.', 'success')
    else:

        driver_post = Rides.query.get_or_404(match_id)
        driver_post.status = 'CANCELED'
        db.session.commit()
        flash('Driver post has been canceled.', 'success')

    return redirect(url_for('main.booking_history'))


@bp.route('/cancel_match_p/<int:match_id>', methods=['POST'])
def cancel_match_p(match_id):
    match = PassengerMatch.query.get(match_id)
    if match:
        match.status = 'CANCELED'
        db.session.commit()

    return redirect(url_for('main.booking_history'))


#set up view detail page 
@bp.route('/view_detail_d/<int:match_id>', methods=['GET', 'POST'])
@login_required
def view_detail_d(match_id):
    match = PassengerMatch.query.get_or_404(match_id)
    return redirect(url_for('main.match_passenger', driver_id=match.driver_id))

@bp.route('/view_detail_p/<int:match_id>', methods=['GET', 'POST'])
@login_required
def view_detail_p(match_id):
    match = PassengerMatch.query.get_or_404(match_id)
    return redirect(url_for('main.match_drivers', driver_id=match.driver_id))

@bp.route('/upload/<int:match_id>', methods=['GET', 'POST'])
@login_required
def upload_payment_proof(match_id):
    form = PaymentForm()
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    
    if form.validate_on_submit():
        payment_method = form.payment_method.data

        if payment_method == 'upload':
            file = form.payment_proof.data
            filename = secure_filename(file.filename)
            upload_path = os.path.join('web', 'static', 'payment')

            # Ensure upload directory exists
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)

            file_path = os.path.join(upload_path, filename)
            file.save(file_path)

            # Save the payment proof details to the database
            payment_proof = PaymentProof(
                file_name=filename,
                user_id=current_user.id  # Ensure user_id is set
            )
            db.session.add(payment_proof)
            db.session.commit()

            flash('Payment proof uploaded successfully!', 'success')
        elif payment_method == 'cash':
            flash('You have chosen to pay by cash.', 'info')

        # Redirect to booking history or another relevant page
        return redirect(url_for('main.booking_history'))
    
    return render_template('upload.html', form=form, profile=profile, match_id=match_id)
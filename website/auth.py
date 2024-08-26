from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Driverspost, Profile,PassengerMatch
from . import db

bp = Blueprint('main', __name__)

@bp.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')

        user=User.query.filter_by(email=email).first()
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

@bp.route('/')
def home():
    return render_template('home.html',user=current_user)

@bp.route('/forgotpassword')
def forgotpassword():
    return render_template('forgotpassword.html',user=current_user)


@bp.route('/profile',methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':

        fullName=request.form['fullName']
        gender = request.form['gender']
        contact = request.form['contact']


        new_Profile = Profile(
            fullName=fullName,
            gender=gender,
            contact=contact,
            user_id=current_user.id

        )

        db.session.add(new_Profile)
        db.session.commit()

        return redirect(url_for('main.chooseid'))

    return render_template('profile.html')

@bp.route('/bookinghisto')
@login_required
def bookinghisto():
    return render_template('bookinghisto.html', user=current_user)

@bp.route('/chooseid', methods=['GET', 'POST'])
@login_required
def chooseid():
    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'passenger':
            return redirect(url_for('main.drivers_list'))
        elif role == 'driver':
            return redirect(url_for('main.driver_post'))
    return render_template('chooseid.html')



@bp.route('/googlemap')
@login_required
def googlemap():
    return render_template('googlemap.html', user=current_user)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/signup',methods=['GET','POST'])
def sign_up():
    if request.method=='POST':
        email=request.form.get('email')
        password1=request.form.get('password1')
        password2=request.form.get('password2')

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
        else:
            new_user=User(email=email,password=generate_password_hash(password1,method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            #login_user(user,remember=True)
            #flash('Account created.', category='success')
            #return redirect(url_for('main.home'))
            #add user to database
            user = User.query.filter_by(email=email).first()

            if user:  # Check if user is found
                login_user(user, remember=True)
                flash('Account created successfully!', category='success')
                return redirect(url_for('main.profile'))
            else:
                flash('Error during user creation. Please try again.', category='error')

        

    return render_template("signup.html",user=current_user)


@bp.route('/about')
def about():
    return render_template('about.html', user=current_user)




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
            user_id=current_user.id


        )

        db.session.add(new_Driverspost)
        db.session.commit()

        return redirect(url_for('main.match_passenger',driver_id=current_user.id))

    return render_template('driver_post.html')

@bp.route('/drivers_list')
@login_required
def drivers_list():
    drivers = Driverspost.query.all()
    profiles = Profile.query.all()
    profile_dict = {profile.user_id: profile for profile in profiles}

    print("Profile Dict:", profile_dict)
    for driver in drivers:
        print(f"Driver ID: {driver.id}, User ID: {driver.user_id}")

    return render_template('drivers_list.html', drivers=drivers, profile_dict=profile_dict)


@bp.route('/match_passenger/<int:driver_id>')
@login_required
def match_passenger(driver_id):
    driver = Driverspost.query.get_or_404(driver_id)
    profiles = Profile.query.all()
    profile_dict = {profile.user_id: profile for profile in profiles}
    passengers = PassengerMatch.query.filter_by(driver_id=driver_id).all()  
    return render_template('match_passenger.html', driver=driver, passengers=passengers,profile_dict=profile_dict)

@bp.route('/match_driver/<int:driver_id>')
@login_required
def match_driver(driver_id):
    driver = Driverspost.query.get_or_404(driver_id)
    profiles = Profile.query.all()
    profile_dict = {profile.user_id: profile for profile in profiles}
    passengers = PassengerMatch.query.filter_by(driver_id=driver_id).all() 
    return render_template('match_driver.html', driver=driver, passengers=passengers,profile_dict=profile_dict)

@bp.route('/select_driver/<int:driver_id>', methods=['POST'])
@login_required
def select_driver(driver_id):
    selected_driver = Driverspost.query.get_or_404(driver_id)
    
    existing_match = PassengerMatch.query.filter_by(passenger_id=current_user.id, driver_id=driver_id).first()
    if existing_match:
        flash('You have already selected this driver.', 'info')
        return redirect(url_for('main.drivers_list'))
    
    passenger_match = PassengerMatch(passenger_id=current_user.id, driver_id=selected_driver.id)
    db.session.add(passenger_match)
    db.session.commit()
    
    flash('Driver selected successfully.', 'success')
    return redirect(url_for('main.match_driver', driver_id=driver_id))

@bp.route('/remove_passenger/<int:passenger_id>/<int:driver_id>', methods=['POST'])
@login_required
def remove_passenger(passenger_id, driver_id):
    passenger_match = PassengerMatch.query.filter_by(passenger_id=passenger_id, driver_id=driver_id).first_or_404()
    if passenger_match.passenger_id == current_user.id or current_user.has_role('admin'):  # Add a condition to allow admin or the driver
        db.session.delete(passenger_match)
        db.session.commit()
        flash('Passenger removed successfully', 'success')
    return redirect(url_for('main.match_passenger', driver_id=driver_id))



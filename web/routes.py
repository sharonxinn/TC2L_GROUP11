from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Driverspost, Profile
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

@bp.route('/chooseid')
@login_required
def chooseid():
    return render_template('chooseid.html', user=current_user)



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

        return redirect(url_for('main.drivers_list'))

    return render_template('driver_post.html')

@bp.route('/drivers')
@login_required
def drivers_list():
    drivers = Driverspost.query.all()
    profiles = Profile.query.all()
    profile_dict = {profile.user_id: profile for profile in profiles}

    return render_template('drivers_list.html', drivers=drivers, profile_dict=profile_dict)

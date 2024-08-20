from flask import Blueprint,render_template,request,flash,redirect,url_for
from .models import User,Carpool
from werkzeug.security import generate_password_hash,check_password_hash
from . import db
from flask_login import login_user,login_required,logout_user,current_user

auth = Blueprint('auth',__name__)

#define login route
@auth.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')

        user=User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully',category='success')
                login_user(user,remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password,try again',category='error')
        else:
            flash('Email does not exist.',category='error')
    
    return render_template("login.html",user=current_user)

#define profile route
@auth.route('/profile')
@login_required
def profile():
    
    return render_template('profile.html', user=current_user)

#define bookinghisto route
@auth.route('/bookinghisto')
@login_required
def bookinghisto():
    return render_template('bookinghisto.html', user=current_user)


@auth.route('/passenger_post', methods=['GET', 'POST'])
def passenger_post():
    if request.method == 'POST':

        fullName = request.form['fullName']
        gender = request.form['gender']
        dateandTime = request.form['dateandTime']
        pickup = request.form['pickup']
        dropoff = request.form['dropoff']
        totalperson = request.form['totalperson']
        message = request.form['message']

        new_carpool = Carpool(
            fullName=fullName,
            gender=gender,
            dateandTime=dateandTime,
            pickup=pickup,
            dropoff=dropoff,
            totalperson=totalperson,
            message=message
        )

        db.session.add(new_carpool)
        db.session.commit()

        return redirect(url_for('passenger_post'))

    return render_template('passenger_post.html')


#define googlemap route
@auth.route('/map')
@login_required
def map():
    return render_template('map.html', user=current_user)

#define logout route
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

#define sign up route
@auth.route('/signup',methods=['GET','POST'])
def sign_up():
    if request.method=='POST':
        email=request.form.get('email')
        first_name=request.form.get('firstName')
        password1=request.form.get('password1')
        password2=request.form.get('password2')

        user=User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists',category='error')
        elif len(email)<4:
            flash('Email must be greater than 3 characters.',category='error')
        elif len(first_name)<2:
            flash('First Name must be greater than 1 characters.',category='error')
        elif password1 != password2:
            flash('Password does not match.',category='error')
        elif len(password1)<7:
            flash('Password must be greater than 6 characters.',category='error')
        else:
            new_user=User(email=email,first_name=first_name,password=generate_password_hash(password1,method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            #login_user(user,remember=True)
            #flash('Account created.', category='success')
            #return redirect(url_for('views.home'))
            #add user to database
            user = User.query.filter_by(email=email).first()

            if user:  # Check if user is found
                login_user(user, remember=True)
                flash('Account created successfully!', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Error during user creation. Please try again.', category='error')

        

    return render_template("signup.html",user=current_user)

#define about route
@auth.route('/about')
def about():
    return render_template('about.html', user=current_user)

#define change password route
@auth.route('/change_password',methods=['GET','POST'])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')

        if old_password == new_password:
            flash("Old Password and New Password Are The Same.", category='error')

        elif new_password != confirm_new_password:
            flash("New Passwords Don't Match.",category="error")

        elif check_password_hash(current_user.password, old_password):
            current_user.password = generate_password_hash(new_password,method='scrypt')
            db.session.commit()
            flash('Password successfully changed.',category='success')

        else:
            db.session.rollback()
            flash("Incorrect old password.",category='error')


    return render_template('change_password.html',current_page='change_password')
from flask import Blueprint,render_template,request,flash,redirect,url_for
from .models import User
from werkzeug.security import generate_password_hash,check_password_hash
from . import db
from flask_login import login_user,login_required,logout_user,current_user

auth = Blueprint('auth',__name__)

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

@auth.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)
@auth.route('/bookinghisto')
@login_required
def bookinghisto():
    return render_template('bookinghisto.html', user=current_user)
@auth.route('/driverprofile')
@login_required
def driverprofile():
    return render_template('driverprofile.html', user=current_user)

@auth.route('/passengerprofile')
@login_required
def passengerprofile():
    return render_template('passengerprofile.html', user=current_user)

@auth.route('/googlemap')
@login_required
def googlemap():
    return render_template('googlemap.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

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

@auth.route('/about')
def about():
    return render_template('about.html', user=current_user)
# define route for changing password
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


    return render_template('change_password.html',user='current_user')
from flask import Blueprint, render_template, request, flash, redirect, url_for
from auth.models import db, User
from flask_login import current_user
from werkzeug.utils import secure_filename
from PIL import Image
import os

user = Blueprint('user',__name__,template_folder="templates",static_folder="static")


def file_is_valid(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'png', 'jpeg'}


@user.route('/customize_profile', methods=["GET","POST"])
def customize_profile():
    if request.method == "POST":
        
        if 'profile_pic' in request.files:
            profile_pic = request.files['profile_pic']
            
            if profile_pic.filename != "":
                if not file_is_valid(profile_pic.filename):
                    flash("Invalid File Type: Only .jpg, .jpeg and .png Files Are Allowed.",category="error")
                
                else:
                    cwd = os.getcwd()

                    #  if user's original pic is not the default, delete it
                    previous_profile_pic = current_user.profile_pic
                    if previous_profile_pic != "default_pfp.png":
                        os.remove(f"{cwd}/user/static/assets/images/user_uploads/{previous_profile_pic}")

                    filename = secure_filename(profile_pic.filename)
                    os.makedirs(f"{cwd}/user/static/assets/images/user_uploads", exist_ok=True)

                    # resize image (make image smaller so it takes up less space) 
                    img_size = (100,100)
                    i = Image.open(profile_pic)
                    i.thumbnail(img_size)

                    i.save(os.path.join(f"{cwd}/user/static/assets/images/user_uploads", filename))
                    current_user.profile_pic = filename
                    db.session.commit()
                    flash("Profile Picture Successfully Updated!",category='success')

        old_bio = current_user.bio
        new_bio = request.form.get('bio')
        
        if old_bio != new_bio:
            if new_bio is not None and new_bio.strip() != "":
                current_user.bio = new_bio 
                db.session.commit()
                flash("Bio Successfully Updated!",category='success')
                return redirect(url_for('user_bp.customize_profile'))
            
            else:
                current_user.bio = None 
                db.session.commit()
                flash("Bio Successfully Cleared!",category="success")
                
        old_username = current_user.username
        new_username = request.form.get("username")

        new_username_is_taken = User.query.filter_by(username=new_username).first()
        if new_username_is_taken:
            flash("Oops! Username already taken. Please enter a different username.",category="error")
            return redirect(url_for("user_bp.customize_profile"))

        if old_username != new_username and new_username is not None:
            current_user.username = new_username 
            db.session.commit()
            flash("Username successfully changed!",category='success')
            return redirect(url_for('user_bp.customize_profile'))

    current_bio = current_user.bio
    current_profile_pic = current_user.profile_pic 
    current_username = current_user.username
    return render_template('customize_profile.html',
                           current_page="customize_profile",
                           current_profile_pic=current_profile_pic,
                           current_bio=current_bio,
                           current_username=current_username)
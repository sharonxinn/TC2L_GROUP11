from flask_login import current_user, logout_user
from flask_admin import AdminIndexView, BaseView,expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from flask import flash, redirect, url_for
from markupsafe import Markup
from .models import Profile,Rides
from . import db  # Ensure this import is at the bottom to avoid circular import
import os

class AdminIndex(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    
    def can_edit(self):
        return True
    
    def can_delete(self):
        return True
    
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    
    def can_edit(self):
        return True
    
    def can_delete(self):
        return True
    
    def can_create(self):
        return True

class ProfileModelView(ModelView):
    column_list = ('fullName', 'gender', 'contact', 'profile_pic', 'is_approved')
    column_labels = {
        'fullName': 'Full Name',
        'profile_pic': 'Profile Picture',
        'status': 'Status'
    }
    form_columns = ('fullName', 'gender', 'contact', 'profile_pic', 'status')
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    
    def _format_image(view, context, model, name):
        if getattr(model, name):
            return Markup(f'<img src="{url_for("static", filename="" + model.profile_pic)}" width="100" height="100" />')
        return ''

    column_formatters = {
        'profile_pic': _format_image
    }

    @action('reject', 'Reject', 'Are you sure you want to reject the selected profiles?')
    def action_reject(self, ids):
        try:
            query = Profile.query.filter(Profile.id.in_(ids))
            count = 0
            for post in query.all():
                post.status = 'rejected'
                count += 1
            db.session.commit()
            flash(f'{count} driver post(s) successfully rejected.', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            db.session.rollback()

class RiderPostModelView(ModelView):
    column_list = ('dateandTime', 'start_location', 'end_location', 'carplate', 'carmodel', 'totalperson', 'fees', 'message', 'status')
    column_labels = {
        'dateandTime': 'Date and Time',
        'start_location': 'start_location Location',
        'end_location': 'end_location Location',
        'carplate': 'Car Plate',
        'carmodel': 'Car Model',
        'totalperson': 'Total Persons',
        'fees': 'Fees',
        'message': 'Message',
        'status': 'Status'
    }
    form_columns = ('dateandTime', 'start_location', 'start_location_lat', 'start_location_lng', 'end_location', 'end_location_lat', 'end_location_lng', 'carplate', 'carmodel', 'totalperson', 'fees', 'duitnowid', 'message', 'status')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    @action('approve', 'Approve', 'Are you sure you want to approve the selected driver posts?')
    def action_approve(self, ids):
        try:
            query = Rides.query.filter(Rides.id.in_(ids))
            count = 0
            for post in query.all():
                post.status = 'approved'
                count += 1
            db.session.commit()
            flash(f'{count} driver post(s) successfully approved.', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            db.session.rollback()

    @action('reject', 'Reject', 'Are you sure you want to reject the selected driver posts?')
    def action_reject(self, ids):
        try:
            query = Rides.query.filter(Rides.id.in_(ids))
            count = 0
            for post in query.all():
                post.status = 'rejected'
                count += 1
            db.session.commit()
            flash(f'{count} driver post(s) successfully rejected.', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            db.session.rollback()


class AdminLogoutView(BaseView):
    @expose('/')
    def logout_admin(self):
        logout_user()
        flash("Logged Out Successfully!", category='success')
        return redirect(url_for('main.login'))

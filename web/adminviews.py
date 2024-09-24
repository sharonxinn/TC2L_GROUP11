from flask_login import current_user, logout_user
from flask_admin import AdminIndexView, BaseView,expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from flask import flash, redirect, url_for
from markupsafe import Markup
from .models import Profile,Rides,PassengerMatch
from . import db  
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
    column_list = ('fullName', 'gender', 'contact', 'status')
    column_labels = {
        'fullName': 'Full Name',
        'status': 'Status'
    }
    form_columns = ('fullName', 'gender', 'contact', 'status')
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    @action('reject', 'Reject', 'Are you sure you want to reject the selected profiles?')
    def action_reject(self, ids):
        try:
            query = Profile.query.filter(Profile.id.in_(ids))
            count = 0
            for post in query.all():
                post.status = 'REJECTED'
                count += 1
            db.session.commit()
            flash(f'{count} driver post(s) successfully rejected.', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            db.session.rollback()

class RiderPostModelView(ModelView):
    column_list = ('dateandTime', 'start_location', 'end_location', 'carplate', 'carmodel', 'totalperson', 'fees', 'message', 'status', 'matched_passengers')  # Added 'matched_passengers'
    column_labels = {
        'dateandTime': 'Date and Time',
        'start_location': 'Start Location',
        'end_location': 'End Location',
        'carplate': 'Car Plate',
        'carmodel': 'Car Model',
        'totalperson': 'Total Persons',
        'fees': 'Fees',
        'message': 'Message',
        'status': 'Status',
        'matched_passengers': 'Matched Passengers'  # New label for matched passengers
    }
    form_columns = ('dateandTime', 'start_location', 'start_location_lat', 'start_location_lng', 'end_location', 'end_location_lat', 'end_location_lng', 'carplate', 'carmodel', 'totalperson', 'fees', 'duitnowid', 'message', 'status')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    # Custom formatter to display matched passengers
    def _matched_passengers_formatter(self, context, model, name):
        matches = PassengerMatch.query.filter_by(driver_id=model.id).all()
        if matches:
            passengers = [f'{match.passenger.email}' for match in matches]
            return ', '.join(passengers)
        else:
            return 'No passengers matched yet.'

    # Add the formatter for the 'matched_passengers' column
    column_formatters = {
        'matched_passengers': _matched_passengers_formatter
    }

    @action('approve', 'Approve', 'Are you sure you want to approve the selected driver posts?')
    def action_approve(self, ids):
        try:
            query = Rides.query.filter(Rides.id.in_(ids))
            count = 0
            for post in query.all():
                post.status = 'APPROVED'
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
                post.status = 'REJECTED'
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

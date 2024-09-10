from flask_wtf import FlaskForm
from wtforms import IntegerField,TextAreaField, RadioField, FileField, SubmitField
from wtforms.validators import DataRequired

class PaymentForm(FlaskForm):
    payment_method = RadioField('Payment Method', choices=[('upload', 'Upload Payment Proof'), ('cash', 'Pay by Cash')], default='upload', validators=[DataRequired()])
    payment_proof = FileField('Payment Proof')
    submit = SubmitField('Submit')

class RatingForm(FlaskForm):
    rating = IntegerField('Rating (1-5)', validators=[DataRequired()])
    feedback = TextAreaField('Feedback')
    submit = SubmitField('Submit')


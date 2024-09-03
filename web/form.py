from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileRequired

class PaymentForm(FlaskForm):
    passenger_name = StringField('Passenger Name', validators=[DataRequired()])
    payment_proof = FileField('Payment Proof', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'pdf'], 'Images and PDFs only!')])
    submit = SubmitField('Upload')

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///passengerpost.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Carpool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(100), nullable=False)
    dateandTime = db.Column(db.String(10), nullable=False)
    pickup = db.Column(db.String(100), nullable=False)
    dropoff = db.Column(db.String(100), nullable=False)
    totalperson = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(100), nullable=False)

# 创建数据库
with app.app_context():
    db.create_all()

@app.route('/passenger_post', methods=['GET', 'POST'])
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

if __name__ == '__main__':
    app.run(debug=True)
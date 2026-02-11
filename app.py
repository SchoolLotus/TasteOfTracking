
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime

#
# App Configuration
#

app = Flask(__name__, template_folder='template')
app.secret_key = 'secretkeyandstuff' # Change this to a random secret key in production

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tastetracker_ps.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#
# Database Models
#

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.Date, default=datetime.utcnow)

    #User review relationship
    #one user can have mutliple reviews
    # backrerf "author" allows us to access the user from the review
    # lazy = True loads reviews on demand
    reviews = db.relationship('Review', backref='author', lazy=True)


class Review(db.Model):
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    restaurant_name = db.Column(db.String(100), nullable=False)
    cuisine_type = db.Column(db.String(50), nullable=False)
    review_date = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.Date, default=datetime.utcnow)

#Home Route - View All Reviews

@app.route("/")
def Home():
     reviews = Review.query.order_by(Review.created_at.desc()).all() #fetch all reviews, newest first
     return render_template("home.html", reviews=reviews) #render home template with reviews

#run app, keep at bottom

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)